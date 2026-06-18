# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pool.c

This file implements ARM3 pool page allocation support: paged-pool virtual allocation through bitmaps and demand-zero PTEs, nonpaged-pool page allocation through free-list descriptors, nonpaged expansion backed by system PTEs and PFNs, protected freed-pool support, pool threshold events, session pool setup, process quota helpers, and mapping-address reservation APIs.

Core globals:
- `MmNonPagedPoolFreeListHead[]` stores nonpaged free blocks bucketed by page count.
- `MmPagedPoolInfo` stores paged-pool PTE bounds, allocation bitmap, end-of-allocation bitmap, hint, and expansion state.
- `MmNumberOfFreeNonPagedPool`, `MmAllocatedNonPagedPool`, and quota totals track pool capacity and accounting.
- `MmProtectFreedNonPagedPool` enables invalidating freed nonpaged pool PTEs to catch use-after-free.
- `MiNonPagedPoolSListHead` and `MiPagedPoolSListHead` cache one-page allocations for fast reuse.

Protected freed-pool support:
- `MiProtectFreeNonPagedPool` invalidates freed pool PTEs and marks them with the prototype bit so faults can be recognized as freed-pool accesses.
- `MiUnProtectFreeNonPagedPool` restores those PTEs when list manipulation needs to touch freed block metadata.
- `MiProtectedPoolUnProtectLinks`, `MiProtectedPoolProtectLinks`, `MiProtectedPoolInsertList`, and `MiProtectedPoolRemoveEntryList` wrap list operations so free-list links remain accessible only while needed.

Initialization:
- `MiInitializeNonPagedPoolThresholds` computes low/high nonpaged-pool thresholds based on maximum pool size.
- `MiInitializePoolEvents` initializes low/high paged and nonpaged pool events from current free capacity.
- `MiInitializeNonPagedPool` initializes S-lists, disables them under freed-pool protection, creates the initial single free block over initial nonpaged pool, marks per-page owners/signatures, records initial pool PFN frame bounds, and initializes nonpaged expansion system PTEs behind guard pages.
- `MiInitializeSessionPool` initializes session paged pool: descriptor, address bounds, PDE/PTE metadata, first page table, allocation bitmap, and end bitmap.

Allocation behavior:
- `MiAllocatePoolPages` handles both paged and nonpaged pool.
- Paged pool uses `RtlFindClearBitsAndSet` over `PagedPoolAllocationMap`, expands by allocating page tables if necessary, writes demand-zero writable PTEs, marks allocation ends in `EndOfPagedPoolBitmap`, and returns virtual space.
- One-page paged-pool allocations may be served from `MiPagedPoolSListHead`.
- Nonpaged pool first tries `MiNonPagedPoolSListHead` for one-page allocations, then searches bucketed free-list entries.
- Nonpaged free blocks are split from the tail of a free entry. PFN flags mark `StartOfAllocation`, `EndOfAllocation`, and optional verifier allocation.
- If initial nonpaged pool has no suitable block, the allocator reserves system PTEs from `NonPagedPoolExpansion`, allocates physical pages, initializes PFNs, writes valid kernel PTEs, and returns the mapped VA.

Free behavior:
- `MiFreePoolPages` handles paged-pool frees by finding allocation length from `EndOfPagedPoolBitmap`, optionally caching one-page frees in the S-list, deleting pageable system VM, and clearing allocation bits.
- Nonpaged frees find the allocation length through PFN `EndOfAllocation`, optionally cache one-page frees, clear PFN allocation flags, and coalesce adjacent free blocks before and after the freed range.
- Free block descriptors use `MM_FREE_POOL_SIGNATURE`, `Size`, `Owner`, and list links on page-aligned chunks.
- Protected-pool mode temporarily unprotects adjacent free descriptors during coalescing and reprotects the final free block.

Quota and mapping-address APIs:
- `MmRaisePoolQuota` raises per-process pool quota under `PspQuotaLock`, with availability checks for nonpaged and paged pool.
- `MmReturnPoolQuota` returns quota to global counters.
- `MmAllocateMappingAddress` reserves system PTEs plus two metadata PTEs storing size and pool tag.
- `MmFreeMappingAddress` validates the tag, size, and that all reserved mapping PTEs are empty before releasing the system PTE range.

Notable limitations and risk points:
- S-list caching returns one-page pool allocations without immediately clearing allocation metadata or deleting backing pages, so correctness depends on callers treating them as same-size page-cache reuse.
- Nonpaged-pool expansion manually initializes PFNs instead of using `MiInitializePfn`, and uses `MI_USAGE_PAGED_POOL` labels even while allocating nonpaged expansion pages.
- Protected freed-pool relies on invalid PTEs marked as prototype; `pagfault.c` recognizes this and bugchecks on freed nonpaged pool modification.
- Paged-pool expansion is constrained by available PDE/PTE range and returns NULL on bitmap/PDE exhaustion.
- Session pool has architecture-specific FIXME behavior around AMD64 page-table recording.
- `MmDeterminePoolType` bugchecks if an address is outside known paged/nonpaged ranges.
