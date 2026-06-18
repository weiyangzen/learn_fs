# File Research: sources/os/linux/linux/mm/internal.h

Large internal MM header collecting cross-file declarations, inline helpers, data structures, and configuration stubs for Linux memory management implementation files.

Major areas covered:
- VMA and page-table movement state via `struct pagetable_move_control` and `PAGETABLE_MOVE()`.
- GFP masks, allocation warning helpers, page writeback, reclaim, and show-mem flags.
- Folio mapping helpers, swap-entry batching, PTE batching for large folios, anon-vma locking/refcounting, and VMA hook safety helpers.
- Page-cache, truncate, reclaim, LRU, mlock, fault, readahead, and address-space invalidation declarations.
- Buddy allocator internals, pageblock helpers, compound folio initialization, page allocation/free declarations, watermarks, CMA, compaction, and sparsemem hooks.
- Memory-failure declarations used by hwpoison injection.
- Vmalloc/ioremap remap preparation, GUP internal flags and COW-unshare rules, soft-dirty helpers, shrinker debug helpers, workingset hooks, mmu-notifier wrappers, and max-map-count access.

Important inline logic:
- `folio_pte_batch_flags()` identifies contiguous PTE batches mapping a large folio while optionally merging dirty/young/write state.
- `swap_pte_batch()` detects contiguous swap PTE batches with matching swap cgroup IDs.
- `page_is_buddy()` and `find_buddy_page_pfn()` encode buddy allocator coalescing rules.
- `gup_must_unshare()` decides when read-only `FOLL_PIN` must break COW/exclusivity.
- `mmap_file()` and `vma_close()` replace VMA hooks with dummy ops after error/close to prevent unsafe later callbacks.

Role:
This header is not one subsystem; it is an internal MM contract surface. Many declarations here connect implementation files across `mm/`, and incorrect changes have broad allocator, reclaim, fault, page-table, and filesystem mmap impact.
