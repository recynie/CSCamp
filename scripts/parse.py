#!/usr/bin/env python3
"""
parse.py — 合并两个数据源，解析为 camps.json + defaults.json
数据源1: shenyanpai/awesome-summer-camp-2026 (全学科 Markdown)
数据源2: CS-BAOYAN/BoardCaster (camp2026, JSON, CS方向)
输出: src/data/camps.json, src/data/defaults.json
"""

import re
import json
import urllib.request
import urllib.parse
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

import yaml

# ── 路径 ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
FILTER_FILE    = ROOT / "filter.yaml"
SCHOOL_TAGS_FILE = ROOT / "school_tags.yaml"
OUTPUT_FILE    = ROOT / "src" / "data" / "camps.json"
DEFAULTS_FILE  = ROOT / "src" / "data" / "defaults.json"

UPSTREAM_SHENYAN  = "https://raw.githubusercontent.com/shenyanpai/awesome-summer-camp-2026/main"
UPSTREAM_BOARDCAST = "https://raw.githubusercontent.com/CS-BAOYAN/BoardCaster/main/data.json"

CATEGORY_FILES = {
    "理工类": "README-理工类.md",
    "经管类": "README-经管类.md",
    "文法类": "README-文法类.md",
    "医农类": "README-医农类.md",
}

ROW_RE = re.compile(
    r"^\|\s*(?P<deadline>[^|]+?)\s*\|\s*\[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\)\s*\|",
    re.MULTILINE,
)
SCHOOL_H3_RE   = re.compile(r"<h3[^>]*>([^<]+)</h3>", re.IGNORECASE)
EXPIRED_DATE_RE = re.compile(r"~~(\d{4}-\d{2}-\d{2})~~")
DATE_RE         = re.compile(r"(\d{4}-\d{2}-\d{2})")

CST = timezone(timedelta(hours=8))


# ── 学校标签表 ────────────────────────────────────────────────────────────────

def load_school_tags() -> tuple[dict[str, list[str]], dict[str, str]]:
    """
    返回:
      school_tags:  {规范名 → [tags]}
      aliases:      {别名 → 规范名}
    """
    with open(SCHOOL_TAGS_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    school_tags: dict[str, list[str]] = {}
    aliases: dict[str, str] = {}

    for entry in data.get("schools", []):
        name = entry["name"]
        tags = entry.get("tags", [])
        school_tags[name] = tags
        for alias in entry.get("aliases", []):
            aliases[alias] = name

    return school_tags, aliases


def normalize_school(name: str, aliases: dict[str, str]) -> str:
    """将别名统一映射到规范学校名"""
    return aliases.get(name, name)


def get_tags(school: str, school_tags: dict[str, list[str]]) -> list[str]:
    return school_tags.get(school, [])


# ── 网络工具 ──────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "CSCamp-sync/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


# ── 解析 shenyanpai Markdown ──────────────────────────────────────────────────

def parse_deadline(raw: str) -> tuple[str | None, bool]:
    raw = raw.strip()
    if raw.lower() in ("暂无", "nan", "", "-"):
        return None, False
    expired_match = EXPIRED_DATE_RE.search(raw)
    if expired_match:
        return expired_match.group(1), True
    date_match = DATE_RE.search(raw)
    if date_match:
        return date_match.group(1), False
    return None, False


def extract_institute(title: str, school: str) -> str:
    cleaned = re.sub(r"^\d{4}年[^\s]*?大学[（(（]?[^）)）]*[）)）]?", "", title).strip()
    if not cleaned:
        cleaned = re.sub(r"^\d{4}年", "", title).strip()
    for kw in ["关于", "举办", "开放", "报名", "招募", "招收", "开始", "启动", "通知", "公告"]:
        idx = cleaned.find(kw)
        if idx > 2:
            cleaned = cleaned[:idx].strip()
            break
    return cleaned or title


def parse_shenyan_readme(
    content: str,
    category: str,
    aliases: dict[str, str],
    school_tags: dict[str, list[str]],
) -> list[dict]:
    entries = []
    current_school = None

    for line in content.split("\n"):
        h3_match = SCHOOL_H3_RE.search(line)
        if h3_match:
            raw_school = h3_match.group(1).strip()
            current_school = normalize_school(raw_school, aliases)
            continue

        row_match = ROW_RE.match(line)
        if row_match and current_school:
            deadline_raw = row_match.group("deadline")
            title        = row_match.group("title").strip()
            url          = row_match.group("url").strip()

            deadline_date, expired = parse_deadline(deadline_raw)
            institute = extract_institute(title, current_school)

            entries.append({
                "school":   current_school,
                "institute": institute,
                "title":    title,
                "url":      url,
                "deadline": deadline_date,
                "expired":  expired,
                "category": category,
                "tags":     get_tags(current_school, school_tags),
                "source":   "shenyanpai",
            })

    return entries


# ── 解析 BoardCaster JSON ─────────────────────────────────────────────────────

def parse_boardcaster(
    raw_data: dict,
    aliases: dict[str, str],
    school_tags: dict[str, list[str]],
) -> list[dict]:
    entries = []
    for item in raw_data.get("camp2026", []):
        raw_school = item.get("name", "").strip()
        school = normalize_school(raw_school, aliases)

        # 解析 ISO 8601 deadline → "YYYY-MM-DD"
        deadline_raw = item.get("deadline", "")
        deadline_date: str | None = None
        expired = False
        if deadline_raw:
            try:
                dt = datetime.fromisoformat(deadline_raw)
                deadline_date = dt.date().isoformat()
                if dt.date() < date.today():
                    expired = True
            except ValueError:
                pass

        # 从 school_tags.yaml 取 tags（修正 BoardCaster 的错误标签）
        tags = get_tags(school, school_tags)
        # 如果 school_tags.yaml 没有收录，回退到 BoardCaster 原始 tags
        if not tags:
            tags = item.get("tags", [])

        desc = item.get("description", "").strip()
        if desc in ("_No response_", ""):
            desc = ""

        entries.append({
            "school":    school,
            "institute": item.get("institute", "").strip(),
            "title":     desc or item.get("institute", "").strip(),
            "url":       item.get("website", "").strip(),
            "deadline":  deadline_date,
            "expired":   expired,
            "category":  "理工类",   # BoardCaster 主要是 CS/理工方向
            "tags":      tags,
            "source":    "boardcaster",
        })

    return entries


# ── urgency ───────────────────────────────────────────────────────────────────

def add_urgency(entries: list[dict]) -> list[dict]:
    today = date.today()
    for e in entries:
        if e["expired"]:
            e["urgency"] = "expired"
        elif e["deadline"] is None:
            e["urgency"] = "unknown"
        else:
            delta = (date.fromisoformat(e["deadline"]) - today).days
            if delta < 0:
                e["urgency"] = "expired"
                e["expired"] = True
            elif delta <= 3:
                e["urgency"] = "critical"
            elif delta <= 7:
                e["urgency"] = "soon"
            elif delta <= 14:
                e["urgency"] = "near"
            else:
                e["urgency"] = "far"
    return entries


# ── 去重合并 ──────────────────────────────────────────────────────────────────

def dedup(entries: list[dict]) -> list[dict]:
    """
    以 url 为主键去重。
    shenyanpai 优先（数据更全），boardcaster 补充不重叠的条目。
    """
    seen: dict[str, dict] = {}
    for e in entries:
        url = e["url"].rstrip("/")
        if url not in seen:
            seen[url] = e
        else:
            # 如果已存在的是 boardcaster，用 shenyanpai 替换（信息更完整）
            if seen[url]["source"] == "boardcaster" and e["source"] == "shenyanpai":
                seen[url] = e
    return list(seen.values())


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    school_tags, aliases = load_school_tags()
    print(f"[tags] 加载 {len(school_tags)} 所学校，{len(aliases)} 个别名")

    # ── 1. shenyanpai ──────────────────────────────────────
    shenyan_entries: list[dict] = []
    for cat, filename in CATEGORY_FILES.items():
        url = f"{UPSTREAM_SHENYAN}/{urllib.parse.quote(filename)}"
        print(f"[fetch] {url}")
        content = fetch(url)
        entries = parse_shenyan_readme(content, cat, aliases, school_tags)
        print(f"  → 解析到 {len(entries)} 条")
        shenyan_entries.extend(entries)

    # ── 2. BoardCaster ─────────────────────────────────────
    print(f"[fetch] {UPSTREAM_BOARDCAST}")
    bc_raw = json.loads(fetch(UPSTREAM_BOARDCAST))
    bc_entries = parse_boardcaster(bc_raw, aliases, school_tags)
    print(f"  → 解析到 {len(bc_entries)} 条 (camp2026)")

    # ── 3. 合并去重（shenyanpai 优先） ─────────────────────
    all_entries = dedup(shenyan_entries + bc_entries)
    print(f"[merge] shenyanpai {len(shenyan_entries)} + boardcaster {len(bc_entries)}"
          f" → 去重后 {len(all_entries)} 条")

    all_entries = add_urgency(all_entries)

    all_entries.sort(key=lambda e: (
        e["deadline"] is None,
        e["expired"],
        e["deadline"] or "9999",
    ))

    # ── 4. 写出 camps.json ─────────────────────────────────
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "updated_at": datetime.now(CST).isoformat(),
        "total": len(all_entries),
        "camps": all_entries,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[done] 写入 {OUTPUT_FILE}  ({len(all_entries)} 条)")

    # ── 5. 写出 defaults.json ──────────────────────────────
    cfg = yaml.safe_load(open(FILTER_FILE, encoding="utf-8"))
    defaults = {
        "categories": cfg.get("default_categories", []),
        "schools":    cfg.get("default_schools", []),
        "tags":       cfg.get("default_tags", []),
        "showExpired": cfg.get("default_show_expired", False),
        "showUnknown": cfg.get("default_show_unknown_deadline", True),
    }
    with open(DEFAULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(defaults, f, ensure_ascii=False, indent=2)
    print(f"[done] 写入 {DEFAULTS_FILE}")


if __name__ == "__main__":
    main()
