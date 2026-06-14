<script lang="ts">
  let {
    title,
    count,
    defaultOpen = false,
    children,
  }: {
    title: string;
    count?: number;
    defaultOpen?: boolean;
    children?: import('svelte').Snippet;
  } = $props();

  // svelte-ignore state_referenced_locally - only used as initial value, never changes
  let open = $state(defaultOpen);
</script>

<div class="bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-800 overflow-hidden">
  <button
    onclick={() => open = !open}
    class="w-full flex items-center justify-between gap-2 px-4 py-3 text-xs font-medium text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
  >
    <span>
      {title}
      {#if count !== undefined}
        <span class="ml-1.5 text-zinc-400 dark:text-zinc-500">
          ({count === 0 ? '全部' : count})
        </span>
      {/if}
    </span>
    <svg
      class="w-3.5 h-3.5 transition-transform {open ? 'rotate-180' : ''}"
      fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  {#if open}
    <div class="px-4 pb-4">
      {@render children?.()}
    </div>
  {/if}
</div>
