<script lang="ts">
  import { filterState, filteredCamps, updatedAt, allCamps, allCategories, allTags } from './lib/store';
  import { getSchools } from './lib/utils';
  import type { Urgency } from './lib/types';
  import Header from './components/Header.svelte';
  import FilterPanel from './components/FilterPanel.svelte';
  import CampList from './components/CampList.svelte';

  let scrollY = $state(0);
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const schools = getSchools(allCamps);
  const urgencyOptions: Urgency[] = ['critical', 'soon', 'near', 'far', 'unknown'];

  function toggleUrgency(u: Urgency) {
    filterState.update(f => {
      const s = new Set(f.urgency);
      s.has(u) ? s.delete(u) : s.add(u);
      return { ...f, urgency: s };
    });
  }

  function toggleCategory(cat: string) {
    filterState.update(f => {
      const s = new Set(f.categories);
      s.has(cat) ? s.delete(cat) : s.add(cat);
      return { ...f, categories: s };
    });
  }

  function toggleTag(tag: string) {
    filterState.update(f => {
      const s = new Set(f.tags);
      s.has(tag) ? s.delete(tag) : s.add(tag);
      return { ...f, tags: s };
    });
  }

  function toggleSchool(school: string) {
    filterState.update(f => {
      const s = new Set(f.schools);
      s.has(school) ? s.delete(school) : s.add(school);
      return { ...f, schools: s };
    });
  }

  function clearFilters() {
    filterState.update(f => ({
      ...f,
      query: '',
      urgency: new Set(),
      categories: new Set(),
      tags: new Set(),
      schools: new Set(),
    }));
  }

  const updatedDate = new Date(updatedAt).toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
</script>

<div class="min-h-screen flex flex-col">
  <Header {updatedDate} totalCount={allCamps.length} filteredCount={$filteredCamps.length} />

  <main class="flex-1 max-w-5xl mx-auto w-full px-4 py-6 gap-6 flex flex-col lg:flex-row">
    <aside class="w-full lg:w-64 shrink-0 lg:sticky lg:top-20 lg:max-h-[calc(100vh-5.5rem)] lg:overflow-y-auto">
      <FilterPanel
        {urgencyOptions}
        {allCategories}
        {allTags}
        {schools}
        filterState={$filterState}
        onToggleUrgency={toggleUrgency}
        onToggleCategory={toggleCategory}
        onToggleTag={toggleTag}
        onToggleSchool={toggleSchool}
        onClearFilters={clearFilters}
        onQueryChange={(q) => filterState.update(f => ({ ...f, query: q }))}
        onToggleExpired={() => filterState.update(f => ({ ...f, showExpired: !f.showExpired }))}
        onToggleUnknown={() => filterState.update(f => ({ ...f, showUnknown: !f.showUnknown }))}
      />
    </aside>

    <section class="flex-1 min-w-0">
      <CampList camps={$filteredCamps} />
    </section>
  </main>

  <footer class="text-center text-xs text-zinc-400 dark:text-zinc-600 py-4">
    数据来源：<a
      href="https://github.com/shenyanpai/awesome-summer-camp-2026"
      target="_blank"
      rel="noopener"
      class="underline hover:text-zinc-600 dark:hover:text-zinc-400"
    >shenyanpai/awesome-summer-camp-2026</a>
    · <a
      href="https://github.com/CS-BAOYAN/BoardCaster"
      target="_blank"
      rel="noopener"
      class="underline hover:text-zinc-600 dark:hover:text-zinc-400"
    >CS-BAOYAN/BoardCaster</a>
    · 每小时自动同步
  </footer>
</div>

<svelte:window bind:scrollY />

{#if scrollY > 300}
  <button
    onclick={scrollToTop}
    aria-label="回到顶部"
    class="fixed bottom-6 right-6 z-50 w-10 h-10 rounded-full bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 shadow-md flex items-center justify-center text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 hover:shadow-lg transition-all"
  >
    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7" />
    </svg>
  </button>
{/if}
