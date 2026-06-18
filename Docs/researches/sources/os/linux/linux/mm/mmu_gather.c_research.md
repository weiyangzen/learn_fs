# File Research: sources/os/linux/linux/mm/mmu_gather.c

TLB gather and deferred page/page-table freeing implementation. This file batches pages and page tables removed from page tables, coordinates TLB shootdowns, delayed rmap removal, RCU table freeing, and final cleanup for unmap/protection teardown paths.

Key responsibilities:
- Provides `tlb_gather_mmu()`, `tlb_gather_mmu_fullmm()`, `tlb_gather_mmu_vma()`, `tlb_flush_mmu()`, and `tlb_finish_mmu()`.
- Batches freed pages through local and allocated `mmu_gather_batch` structures unless `CONFIG_MMU_GATHER_NO_GATHER` is set.
- Supports encoded page entries that can include delayed rmap removal and multi-page folio run lengths.
- Frees batches in bounded chunks to avoid soft lockups, with different chunking when page poisoning or init-on-free increases per-page cost.
- Supports batched page-table freeing under `CONFIG_MMU_GATHER_TABLE_FREE`.
- Uses RCU or IPI synchronization for architectures with lockless software page-table walkers.
- Tracks nested TLB flush situations and forces full-mm/range reset behavior when parallel batching could leave stale translations.

Important behavior:
- `tlb_next_batch()` stops allocating additional batches when delayed rmaps are pending outside the local batch, ensuring delayed rmap processing stays bounded.
- `tlb_flush_rmaps()` removes rmap entries only after a TLB flush, preserving ordering for concurrent users.
- `tlb_remove_table()` batches page-table pages when possible, otherwise performs immediate table invalidation and single-table freeing.
- RCU table freeing uses sched-RCU semantics because lockless page-table walkers rely on IRQ/preempt-disabled sections.
- `tlb_finish_mmu()` warns if fully unshared page tables remain, handles nested flush escalation, flushes TLBs, frees batched pages/tables, releases extra batch pages, and decrements pending flush state.

Dependencies:
- Architecture TLB APIs, page-table allocation/free hooks, RCU, SMP IPIs, hugetlb page size handling, swap cache freeing, folio/page poisoning, rmap removal, and mm pending-TLB-flush counters.

Notable risks:
- Pages and page tables must not be freed before stale CPU or software-walker references are invalidated.
- Delayed rmap removal must remain paired with post-flush processing.
- Nested batched PTE changes can require broader TLB flushing than the nominal range.
- Allocation failure in table batching must still guarantee progress through single-table fallback.
