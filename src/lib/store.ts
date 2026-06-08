import { writable, derived } from 'svelte/store';
import type { Camp, FilterState, CampsData } from './types';
import raw from '$data/camps.json';
import defaultsRaw from '$data/defaults.json';

const data = raw as CampsData;

export const updatedAt = data.updated_at;
export const allCamps: Camp[] = data.camps;

// All unique categories and schools present in the data
export const allCategories: string[] = [...new Set(allCamps.map(c => c.category))].sort();

// All unique tags across all camps, in a canonical order
export const ALL_TAGS = ['TOP2', 'C9', '华五', '985', '211', 'AI强校', '研究院', '港澳', '联培', '双非', '四非'];
export const allTags: string[] = ALL_TAGS.filter(t =>
  allCamps.some(c => c.tags.includes(t))
);

const defaults = defaultsRaw as {
  categories: string[];
  schools: string[];
  tags: string[];
  showExpired: boolean;
  showUnknown: boolean;
};

export const filterState = writable<FilterState>({
  query: '',
  urgency: new Set(),
  categories: new Set(defaults.categories),
  tags: new Set(defaults.tags),
  schools: new Set(defaults.schools),
  showExpired: defaults.showExpired,
  showUnknown: defaults.showUnknown,
});

export const filteredCamps = derived(filterState, ($f) => {
  return allCamps.filter(camp => {
    // 已截止
    if (camp.expired && !$f.showExpired) return false;
    // 日期未知
    if (camp.deadline === null && !$f.showUnknown) return false;
    // 类别
    if ($f.categories.size > 0 && !$f.categories.has(camp.category)) return false;
    // 学校档次 tags（camp 的 tags 与筛选 tags 有交集即通过）
    if ($f.tags.size > 0 && !camp.tags.some(t => $f.tags.has(t))) return false;
    // 学校名过滤
    if ($f.schools.size > 0 && !$f.schools.has(camp.school)) return false;
    // 紧迫度
    if ($f.urgency.size > 0 && !$f.urgency.has(camp.urgency)) return false;
    // 搜索词
    if ($f.query) {
      const q = $f.query.toLowerCase();
      const haystack = `${camp.school} ${camp.institute} ${camp.title}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
});
