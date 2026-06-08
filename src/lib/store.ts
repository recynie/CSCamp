import { writable, derived } from 'svelte/store';
import type { Camp, FilterState } from './types';
import type { CampsData } from './types';
import raw from '$data/camps.json';

const data = raw as CampsData;

export const updatedAt = data.updated_at;
export const allCamps: Camp[] = data.camps;

export const filterState = writable<FilterState>({
  query: '',
  urgency: new Set(),
  schools: new Set(),
  showExpired: false,
  showUnknown: true,
});

export const filteredCamps = derived(filterState, ($f) => {
  return allCamps.filter(camp => {
    // 已截止
    if (camp.expired && !$f.showExpired) return false;
    // 日期未知
    if (camp.deadline === null && !$f.showUnknown) return false;
    // 紧迫度
    if ($f.urgency.size > 0 && !$f.urgency.has(camp.urgency)) return false;
    // 学校
    if ($f.schools.size > 0 && !$f.schools.has(camp.school)) return false;
    // 搜索词
    if ($f.query) {
      const q = $f.query.toLowerCase();
      const haystack = `${camp.school} ${camp.institute} ${camp.title}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
});
