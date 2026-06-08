<script lang="ts">
  import type { Camp } from '../lib/types';
  import { URGENCY_LABELS, URGENCY_COLORS, daysUntil, formatDeadline, formatCountdown } from '../lib/utils';

  let { camps }: { camps: Camp[] } = $props();
</script>

{#if camps.length === 0}
  <div class="flex flex-col items-center justify-center py-24 text-zinc-400 dark:text-zinc-600">
    <span class="text-4xl mb-3">🔍</span>
    <p class="text-sm">没有符合条件的通知</p>
  </div>
{:else}
  <div class="text-xs text-zinc-400 dark:text-zinc-500 mb-3">
    共 {camps.length} 条
  </div>

  <div class="space-y-2">
    {#each camps as camp (camp.url)}
      {@const days = daysUntil(camp.deadline)}
      {@const colors = URGENCY_COLORS[camp.urgency]}
      <div class="bg-white dark:bg-zinc-900 rounded-lg overflow-hidden border border-zinc-200 dark:border-zinc-800 {colors.row} hover:shadow-sm transition-shadow">
        <div class="px-4 py-3">
          <div class="flex items-start justify-between gap-3">
            <!-- Left: school + title -->
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="font-medium text-sm text-zinc-900 dark:text-zinc-100 shrink-0">
                  {camp.school}
                </span>
                <span class="text-xs px-1.5 py-0.5 rounded-full {colors.badge} shrink-0">
                  {URGENCY_LABELS[camp.urgency]}
                </span>
              </div>
              <a
                href={camp.url}
                target="_blank"
                rel="noopener"
                class="text-xs text-zinc-600 dark:text-zinc-400 hover:text-blue-600 dark:hover:text-blue-400 leading-relaxed line-clamp-2 transition-colors"
              >
                {camp.institute || camp.title}
              </a>
            </div>

            <!-- Right: deadline + countdown -->
            <div class="shrink-0 text-right">
              <div class="text-sm font-mono font-medium {camp.expired ? 'text-zinc-400 line-through' : 'text-zinc-800 dark:text-zinc-200'}">
                {formatDeadline(camp.deadline)}
              </div>
              <div class="text-xs {camp.urgency === 'critical' ? 'text-red-500 font-semibold' : 'text-zinc-400 dark:text-zinc-500'} mt-0.5">
                {formatCountdown(days)}
              </div>
            </div>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}
