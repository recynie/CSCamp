<script lang="ts">
  import { URGENCY_LABELS } from '../lib/utils';
  import type { Urgency, FilterState } from '../lib/types';

  let {
    urgencyOptions,
    allCategories,
    schools,
    filterState,
    onToggleUrgency,
    onToggleCategory,
    onToggleSchool,
    onClearFilters,
    onQueryChange,
    onToggleExpired,
    onToggleUnknown,
  }: {
    urgencyOptions: Urgency[];
    allCategories: string[];
    schools: string[];
    filterState: FilterState;
    onToggleUrgency: (u: Urgency) => void;
    onToggleCategory: (c: string) => void;
    onToggleSchool: (s: string) => void;
    onClearFilters: () => void;
    onQueryChange: (q: string) => void;
    onToggleExpired: () => void;
    onToggleUnknown: () => void;
  } = $props();

  let schoolQuery = $state('');
  const filteredSchools = $derived(
    schools.filter(s => s.toLowerCase().includes(schoolQuery.toLowerCase()))
  );

  const hasActiveFilters = $derived(
    !!filterState.query ||
    filterState.urgency.size > 0 ||
    filterState.categories.size > 0 ||
    filterState.schools.size > 0
  );
</script>

<div class="space-y-4">
  <!-- Search -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">搜索</p>
    <input
      type="text"
      value={filterState.query}
      oninput={(e) => onQueryChange(e.currentTarget.value)}
      placeholder="学校、院系、关键词..."
      class="w-full px-3 py-2 text-sm rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>

  <!-- Categories -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">
      类别 ({filterState.categories.size === 0 ? '全部' : filterState.categories.size})
    </p>
    <div class="flex flex-col gap-2">
      {#each allCategories as cat}
        <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 p-1 rounded">
          <input
            type="checkbox"
            checked={filterState.categories.has(cat)}
            onchange={() => onToggleCategory(cat)}
            class="rounded border-zinc-300 dark:border-zinc-600"
          />
          <span class="text-zinc-700 dark:text-zinc-300">{cat}</span>
        </label>
      {/each}
    </div>
  </div>

  <!-- Urgency -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">紧迫度</p>
    <div class="flex flex-col gap-2">
      {#each urgencyOptions as u}
        <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 p-1 rounded">
          <input
            type="checkbox"
            checked={filterState.urgency.has(u)}
            onchange={() => onToggleUrgency(u)}
            class="rounded border-zinc-300 dark:border-zinc-600"
          />
          <span class="text-zinc-700 dark:text-zinc-300">{URGENCY_LABELS[u]}</span>
        </label>
      {/each}
    </div>
  </div>

  <!-- Show/Hide toggles -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">显示选项</p>
    <div class="flex flex-col gap-2">
      <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 p-1 rounded">
        <input
          type="checkbox"
          checked={filterState.showExpired}
          onchange={onToggleExpired}
          class="rounded border-zinc-300 dark:border-zinc-600"
        />
        <span class="text-zinc-700 dark:text-zinc-300">已截止</span>
      </label>
      <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 p-1 rounded">
        <input
          type="checkbox"
          checked={filterState.showUnknown}
          onchange={onToggleUnknown}
          class="rounded border-zinc-300 dark:border-zinc-600"
        />
        <span class="text-zinc-700 dark:text-zinc-300">日期未知</span>
      </label>
    </div>
  </div>

  <!-- Schools -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">
      学校 ({filterState.schools.size === 0 ? '全部' : filterState.schools.size})
    </p>
    <input
      type="text"
      bind:value={schoolQuery}
      placeholder="筛选学校..."
      class="w-full px-3 py-2 text-sm rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
    />
    <div class="max-h-60 overflow-y-auto space-y-1">
      {#each filteredSchools as school}
        <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 p-1 rounded">
          <input
            type="checkbox"
            checked={filterState.schools.has(school)}
            onchange={() => onToggleSchool(school)}
            class="rounded border-zinc-300 dark:border-zinc-600"
          />
          <span class="text-zinc-700 dark:text-zinc-300 text-xs">{school}</span>
        </label>
      {/each}
    </div>
  </div>

  <!-- Clear filters -->
  {#if hasActiveFilters}
    <button
      onclick={onClearFilters}
      class="w-full py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors"
    >
      清除筛选（显示全部）
    </button>
  {/if}
</div>
