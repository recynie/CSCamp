import { writable, derived } from 'svelte/store';
import type { Camp, FilterState } from './types';
import type { CampsData } from './types';
import raw from '$data/camps.json';
import defaultsRaw from '$data/defaults.json';

const data = raw as CampsData;

export const updatedAt = data.updated_at;
export const allCamps: Camp[] = data.camps;

// All unique categories and schools present in the data
export const allCategories: string[] = [...new Set(allCamps.map(c => c.category))].sort();

// Load defaults from defaults.json (generated from filter.yaml)
const defaults = defaultsRaw as {
  categories: string[];
  schools: string[];
  showExpired: boolean;
  showUnknown: boolean;
};

export const filterState = writable<FilterState>({
  query: '',
  urgency: new Set(),
  categories: new Set(defaults.categories),
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
    // 类别（空 = 全部）
    if ($f.categories.size > 0 && !$f.categories.has(camp.category)) return false;
    // 学校（空 = 全部）
    if ($f.schools.size > 0 && !$f.schools.has(camp.school)) return false;
    // 紧迫度（空 = 全部）
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
