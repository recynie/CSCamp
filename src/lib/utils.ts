import type { Camp, Urgency } from './types';

export const URGENCY_LABELS: Record<Urgency, string> = {
  critical: '≤3天',
  soon:     '≤7天',
  near:     '≤14天',
  far:      '14天以上',
  unknown:  '日期未知',
  expired:  '已截止',
};

export const URGENCY_COLORS: Record<Urgency, { badge: string; row: string; dot: string }> = {
  critical: {
    badge: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
    row:   'border-l-4 border-red-400',
    dot:   'bg-red-500 animate-pulse',
  },
  soon: {
    badge: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
    row:   'border-l-4 border-orange-400',
    dot:   'bg-orange-400',
  },
  near: {
    badge: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
    row:   'border-l-4 border-yellow-400',
    dot:   'bg-yellow-400',
  },
  far: {
    badge: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
    row:   'border-l-4 border-green-400',
    dot:   'bg-green-400',
  },
  unknown: {
    badge: 'bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400',
    row:   'border-l-4 border-zinc-300 dark:border-zinc-600',
    dot:   'bg-zinc-400',
  },
  expired: {
    badge: 'bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500',
    row:   'border-l-4 border-zinc-200 dark:border-zinc-700 opacity-50',
    dot:   'bg-zinc-300',
  },
};

export function daysUntil(deadline: string | null): number | null {
  if (!deadline) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const d = new Date(deadline);
  d.setHours(0, 0, 0, 0);
  return Math.round((d.getTime() - today.getTime()) / 86400000);
}

export function formatDeadline(deadline: string | null): string {
  if (!deadline) return '暂无';
  const [, m, d] = deadline.split('-');
  return `${m}/${d}`;
}

export function formatCountdown(days: number | null): string {
  if (days === null) return '—';
  if (days < 0) return `已过期`;
  if (days === 0) return '今天截止';
  return `${days} 天`;
}

/** Get all unique school names from a list of camps */
export function getSchools(camps: Camp[]): string[] {
  return [...new Set(camps.map(c => c.school))].sort((a, b) =>
    a.localeCompare(b, 'zh-CN')
  );
}
