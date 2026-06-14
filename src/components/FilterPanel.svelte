<script lang="ts">
  import { URGENCY_LABELS } from '../lib/utils';
  import type { Urgency, FilterState } from '../lib/types';
  import CollapsibleSection from './CollapsibleSection.svelte';

  let {
    urgencyOptions,
    allCategories,
    allTags,
    allDepartmentGroups,
    schools,
    filterState,
    onToggleUrgency,
    onToggleCategory,
    onToggleTag,
    onToggleDepartmentGroup,
    onToggleSchool,
    onClearFilters,
    onQueryChange,
    onToggleExpired,
    onToggleUnknown,
  }: {
    urgencyOptions: Urgency[];
    allCategories: string[];
    allTags: string[];
    allDepartmentGroups: string[];
    schools: string[];
    filterState: FilterState;
    onToggleUrgency: (u: Urgency) => void;
    onToggleCategory: (c: string) => void;
    onToggleTag: (t: string) => void;
    onToggleDepartmentGroup: (g: string) => void;
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

  let departmentQuery = $state('');
  const filteredDepartmentGroups = $derived(
    allDepartmentGroups.filter(g => g.toLowerCase().includes(departmentQuery.toLowerCase()))
  );

  const hasActiveFilters = $derived(
    !!filterState.query ||
    filterState.urgency.size > 0 ||
    filterState.categories.size > 0 ||
    filterState.tags.size > 0 ||
    filterState.schools.size > 0
  );

  // Tag display colors
  const TAG_COLORS: Record<string, string> = {
    'TOP2':   'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
    'C9':     'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
    '华五':   'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    '985':    'bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300',
    '211':    'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300',
    'AI强校': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
    '研究院': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
    '港澳':   'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
    '联培':   'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
    '双非':   'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400',
    '四非':   'bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500',
  };
  const TAG_COLOR_DEFAULT = 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400';
</script>

<div class="space-y-3">
  <!-- 1. 搜索 — always expanded (no collapse needed, it's just an input) -->
  <div class="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-zinc-200 dark:border-zinc-800">
    <p class="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">搜索</p>
    <input
      type="text"
      value={filterState.query}
      oninput={(e) => onQueryChange(e.currentTarget.value)}
      placeholder="学校、院系、关键词..."
      class="w-full px-3 py-2 text-sm rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>

  <!-- 2. 数据源 — 默认折叠，用 tag 按钮替代 checkbox -->
  <CollapsibleSection title="数据源" count={filterState.categories.size} defaultOpen={false}>
    <div class="flex flex-wrap gap-1.5">
      {#each allCategories as cat}
        {@const active = filterState.categories.has(cat)}
        <button
          onclick={() => onToggleCategory(cat)}
          class="px-2 py-0.5 rounded-full text-xs font-medium border transition-all
            {active
              ? 'bg-blue-100 text-blue-700 border-transparent ring-2 ring-offset-1 ring-blue-400 dark:bg-blue-900/40 dark:text-blue-300 dark:ring-blue-500'
              : 'bg-zinc-50 text-zinc-500 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700 hover:border-zinc-400'}"
        >
          {cat}
        </button>
      {/each}
    </div>
  </CollapsibleSection>

  <!-- 3. 学校档次 -->
  <CollapsibleSection title="学校档次" count={filterState.tags.size} defaultOpen={true}>
    <div class="flex flex-wrap gap-1.5">
      {#each allTags as tag}
        {@const active = filterState.tags.has(tag)}
        <button
          onclick={() => onToggleTag(tag)}
          class="px-2 py-0.5 rounded-full text-xs font-medium border transition-all
            {active
              ? (TAG_COLORS[tag] ?? TAG_COLOR_DEFAULT) + ' border-transparent ring-2 ring-offset-1 ring-blue-400 dark:ring-blue-500'
              : 'bg-zinc-50 text-zinc-500 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700 hover:border-zinc-400'}"
        >
          {tag}
        </button>
      {/each}
    </div>
  </CollapsibleSection>

  <!-- 4. 学校 — 默认折叠（76所学校，垂直空间大） -->
  <CollapsibleSection title="学校" count={filterState.schools.size} defaultOpen={false}>
    <input
      type="text"
      bind:value={schoolQuery}
      placeholder="筛选学校..."
      class="w-full px-3 py-2 text-sm rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
    />
    <div class="max-h-52 overflow-y-auto space-y-0.5">
      {#each filteredSchools as school}
        <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 px-1 py-0.5 rounded">
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
  </CollapsibleSection>

  <!-- 5. 专业大类 — 默认折叠，加搜索框 + 可滚动列表 -->
  <CollapsibleSection title="专业大类" count={filterState.departmentGroups.size} defaultOpen={false}>
    <input
      type="text"
      bind:value={departmentQuery}
      placeholder="筛选专业大类..."
      class="w-full px-3 py-2 text-sm rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
    />
    <div class="max-h-52 overflow-y-auto space-y-0.5">
      {#each filteredDepartmentGroups as group}
        <label class="flex items-center gap-2 text-sm cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800 px-1 py-0.5 rounded">
          <input
            type="checkbox"
            checked={filterState.departmentGroups.has(group)}
            onchange={() => onToggleDepartmentGroup(group)}
            class="rounded border-zinc-300 dark:border-zinc-600"
          />
          <span class="text-zinc-700 dark:text-zinc-300 text-xs">{group}</span>
        </label>
      {/each}
    </div>
  </CollapsibleSection>

  <!-- 6. 紧迫度 -->
  <CollapsibleSection title="紧迫度" count={filterState.urgency.size} defaultOpen={true}>
    <div class="flex flex-col gap-1">
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
  </CollapsibleSection>

  <!-- 7. 显示选项 -->
  <CollapsibleSection title="显示选项" defaultOpen={true}>
    <div class="flex flex-col gap-1">
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
  </CollapsibleSection>

  <!-- Clear -->
  {#if hasActiveFilters}
    <button
      onclick={onClearFilters}
      class="w-full py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors"
    >
      清除筛选（显示全部）
    </button>
  {/if}
</div>
