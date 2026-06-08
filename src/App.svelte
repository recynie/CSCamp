<script lang="ts">
  import { filterState, filteredCamps, updatedAt, allCamps } from './lib/store';
  import { getSchools, URGENCY_LABELS } from './lib/utils';
  import type { Urgency } from './lib/types';
  import Header from './components/Header.svelte';
  import FilterPanel from './components/FilterPanel.svelte';
  import CampList from './components/CampList.svelte';

  const schools = getSchools(allCamps);

  // urgency options to show (exclude expired — handled by toggle)
  const urgencyOptions: Urgency[] = ['critical', 'soon', 'near', 'far', 'unknown'];

  function toggleUrgency(u: Urgency) {
    filterState.update(f => {
      const s = new Set(f.urgency);
      s.has(u) ? s.delete(u) : s.add(u);
      return { ...f, urgency: s };
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
      schools: new Set(),
    }));
  }

  // format updated_at
  const updatedDate = new Date(updatedAt).toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
</script>

<div class="min-h-screen flex flex-col">
  <Header {updatedDate} totalCount={allCamps.length} />

  <main class="flex-1 max-w-5xl mx-auto w-full px-4 py-6 gap-6 flex flex-col lg:flex-row">
    <aside class="w-full lg:w-64 shrink-0">
      <FilterPanel
        {urgencyOptions}
        {schools}
        filterState={$filterState}
        onToggleUrgency={toggleUrgency}
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
    · 每小时自动同步
  </footer>
</div>
