# File Research: sources/os/linux/linux/mm/swap.c

## Purpose
Implements core folio LRU batching, activation/deactivation/lazyfree transitions, batched folio release, memcg LRU reparenting, and VM swap clustering sysctl setup. Despite the filename, this is primarily LRU/page-cache folio lifecycle code rather than swap slot allocation.

## Main Interfaces
- Folio release: `__folio_put()`, `folios_put_refs()`, `release_pages()`, `__folio_batch_release()`.
- LRU operations: `folio_add_lru()`, `folio_add_lru_vma()`, `folio_mark_accessed()`, `folio_activate()`, `folio_deactivate()`, `deactivate_file_folio()`, `folio_mark_lazyfree()`, `folio_rotate_reclaimable()`.
- Drain operations: `lru_add_drain()`, `lru_add_drain_cpu()`, `lru_add_drain_all()`, `lru_cache_disable()`.
- Cost accounting: `lru_note_cost_unlock_irq()`, `lru_note_cost_refault()`.
- Setup: `swap_setup()` and the `vm/page-cluster` sysctl.

## Control Flow
Per-CPU `cpu_fbatches` collect folios for LRU add, activation, file deactivation, anonymous deactivation, lazyfree, and tail rotation. Operations take a folio reference, queue it into the current CPU batch, and drain when the batch fills or LRU caching is disabled.

Draining locks the target `lruvec`, performs the requested move, updates folio LRU flags and VM/memcg counters, then drops queued folio references in bulk. SMP global draining uses a generation counter and per-CPU workqueue to avoid missed batches under concurrent callers.

Folio release removes folios from LRU, handles zone-device and hugetlb special cases, uncharges memcg, frees deferred split state, and returns pages in batches to the allocator.

## State And Synchronization
Uses local locks for per-CPU folio batches, IRQ-disabling local lock for reclaimable tail rotation, lruvec locks for list mutation, RCU for LRU disable synchronization, and memcg LRU state for reparenting. Multi-gen LRU builds use reference-generation bits instead of classic active/referenced transitions.

## Dependencies
Depends on memcg, workingset, mlock, buffer-head LRU draining, page idle tracking, folio batching, page allocator freeing, and tracepoints from `trace/events/pagemap.h`.

## Risks And Review Focus
- LRU batch draining has subtle barriers and generation logic to prevent missed remote batches.
- Activation of folios still in a local add batch must avoid modifying remote batches and accounting incorrectly.
- `lru_cache_disable()` depends on RCU/preemption guarantees before migration or isolation.
