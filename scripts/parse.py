#!/usr/bin/env python3
"""
parse.py — 从 awesome-summer-camp-2026 拉取 README，解析为 camps.json
用法: python scripts/parse.py
输出: src/data/camps.json
"""

import re
import json
import urllib.request
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

import yaml  # pip install pyyaml

# ── 路径 ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
FILTER_FILE = ROOT / "filter.yaml"
OUTPUT_FILE = ROOT / "src" / "data" / "camps.json"

UPSTREAM = "https://raw.githubusercontent.com/shenyanpai/awesome-summer-camp-2026/main"

CATEGORY_FILES = {
    "理工类": "README-理工类.md",
    "经管类": "README-经管类.md",
    "文法类": "README-文法类.md",
    "医农类": "README-医农类.md",
}

# ── 解析 markdown 表格行 ───────────────────────────────────────────────────────
# 格式: | 截止时间 | [通知标题](url) |
# 截止时间可能是: 2026-06-20 | 暂无 | ~~2026-05-31~~
ROW_RE = re.compile(
    r"^\|\s*(?P<deadline>[^|]+?)\s*\|\s*\[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\)\s*\|",
    re.MULTILINE,
)
SCHOOL_H3_RE = re.compile(r"<h3[^>]*>([^<]+)</h3>", re.IGNORECASE)
EXPIRED_DATE_RE = re.compile(r"~~(\d{4}-\d{2}-\d{2})~~")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

CST = timezone(timedelta(hours=8))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "CSCamp-sync/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def parse_deadline(raw: str) -> tuple[str | None, bool]:
    """
    返回 (ISO日期字符串或None, 是否已截止)
    已截止 = 原文用 ~~...~~ 标记
    """
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


def parse_readme(content: str, category: str) -> list[dict]:
    entries = []
    current_school = None

    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测学校标题 <h3>学校名</h3>
        h3_match = SCHOOL_H3_RE.search(line)
        if h3_match:
            current_school = h3_match.group(1).strip()
            i += 1
            continue

        # 检测表格行
        row_match = ROW_RE.match(line)
        if row_match and current_school:
            deadline_raw = row_match.group("deadline")
            title = row_match.group("title").strip()
            url = row_match.group("url").strip()

            deadline_date, expired = parse_deadline(deadline_raw)

            # 从标题中提取院系（去掉年份前缀 "2026年XXX大学"）
            institute = extract_institute(title, current_school)

            entries.append({
                "school": current_school,
                "institute": institute,
                "title": title,
                "url": url,
                "deadline": deadline_date,          # None 或 "YYYY-MM-DD"
                "expired": expired,
                "category": category,
            })

        i += 1

    return entries


def extract_institute(title: str, school: str) -> str:
    """从通知标题中提取院系名称"""
    # 去掉 "2026年XXX大学" 前缀
    cleaned = re.sub(r"^\d{4}年[^\s]*?大学[（(（]?[^）)）]*[）)）]?", "", title).strip()
    if not cleaned:
        cleaned = re.sub(r"^\d{4}年", "", title).strip()
    # 截取到第一个动词关键词前
    for kw in ["关于", "举办", "开放", "报名", "招募", "招收", "开始", "启动", "通知", "公告"]:
        idx = cleaned.find(kw)
        if idx > 2:
            cleaned = cleaned[:idx].strip()
            break
    return cleaned or title


def load_filter() -> dict:
    with open(FILTER_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_filter(entries: list[dict], cfg: dict) -> list[dict]:
    allowed = set(cfg.get("allowed_schools", []))
    show_expired = cfg.get("show_expired", False)
    show_unknown = cfg.get("show_unknown_deadline", True)

    result = []
    for e in entries:
        # 学校白名单
        if allowed and e["school"] not in allowed:
            continue
        # 已截止过滤
        if e["expired"] and not show_expired:
            continue
        # 截止日期未知过滤
        if e["deadline"] is None and not show_unknown:
            continue
        result.append(e)
    return result


def add_urgency(entries: list[dict]) -> list[dict]:
    """附加 urgency 字段，供前端配色使用"""
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


def main():
    cfg = load_filter()
    categories = cfg.get("categories", list(CATEGORY_FILES.keys()))

    all_entries = []
    for cat in categories:
        filename = CATEGORY_FILES.get(cat)
        if not filename:
            print(f"[warn] 未知类别: {cat}")
            continue
        url = f"{UPSTREAM}/{urllib.parse.quote(filename)}"
        print(f"[fetch] {url}")
        content = fetch(url)
        entries = parse_readme(content, cat)
        print(f"  → 解析到 {len(entries)} 条")
        all_entries.extend(entries)

    filtered = apply_filter(all_entries, cfg)
    print(f"[filter] {len(all_entries)} → {len(filtered)} 条")

    filtered = add_urgency(filtered)

    # 排序：先按截止日期升序，None 排最后
    filtered.sort(key=lambda e: (
        e["deadline"] is None,
        e["expired"],
        e["deadline"] or "9999",
    ))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "updated_at": datetime.now(CST).isoformat(),
        "total": len(filtered),
        "camps": filtered,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[done] 写入 {OUTPUT_FILE}  ({len(filtered)} 条)")


# urllib.parse 需要单独导入
import urllib.parse  # noqa: E402

if __name__ == "__main__":
    main()
