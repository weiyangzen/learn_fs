# File Research: sources/os/linux/linux/mm/rmap.c

## Purpose

`mm/rmap.c` implements reverse mapping: finding virtual mappings for physical folios/pages. It manages anonymous VMA ancestry, file and anon rmap walks, mapcount accounting, referenced/dirty/write-protect operations, reclaim unmapping, migration entry installation, device-exclusive mappings, and hugetlb anonymous rmap support.

Reverse mapping is essential for reclaim, migration, page aging, dirty tracking, COW, KSM, mlock, memory failure, and filesystem-backed page-cache invalidation/writeback interactions.

## Locking Context

The file begins with an explicit lock ordering comment covering `inode->i_rwsem`, `mmap_lock`, mapping invalidate locks, folio lock, hugetlb locks, VMA write locks, `mapping->i_mmap_rwsem`, `anon_vma->rwsem`, page-table locks, swap locks, LRU locks, inode locks, writeback locks, and related ordering. Many routines depend on this hierarchy to avoid reclaim/writeback/fault deadlocks.

## Anonymous VMA Lifecycle

Anonymous rmap state uses:

- `struct anon_vma`
- `struct anon_vma_chain`
- `anon_vma_cachep`
- `anon_vma_chain_cachep`

Key functions:

- `anon_vma_alloc()` initializes refcount, parent/root pointers, and active-child counters.
- `anon_vma_free()` synchronizes against `folio_lock_anon_vma_read()` before freeing RCU-safe slabs.
- `__anon_vma_prepare()` attaches an anon_vma to a VMA, reusing mergeable neighbor anon_vmas when possible.
- `anon_vma_clone()` duplicates anon_vma chains for merge/split/mremap/fork.
- `anon_vma_fork()` attaches child VMAs to parent anon_vmas and creates/reuses child anon_vmas for future COW pages.
- `unlink_anon_vmas()` removes VMA links, updates active/child counts, and releases empty anon_vmas.
- `anon_vma_init()` creates the slab caches.

The fork path uses anon_vma hierarchy roots so rmap can find non-COWed pages across parent/child processes while allowing COWed pages to move to a more specific anon_vma.

## Stable Anon-VMA Lookup

`folio_get_anon_vma()` and `folio_lock_anon_vma_read()` obtain a stable anon_vma from a locked mapped folio. Because anon_vmas are `SLAB_TYPESAFE_BY_RCU`, the code combines RCU, mapcount checks, refcount increments, and rwsem locking to avoid use-after-free when folios are concurrently unmapped.

`folio_lock_anon_vma_read()` has a fast trylock path and a contended/try-lock mode used by reclaim-style walkers that should not block.

## Batched TLB Flush Support

Under `CONFIG_ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH`, the file implements:

- `try_to_unmap_flush()`
- `try_to_unmap_flush_dirty()`
- `set_tlb_ubc_flush_pending()`
- `should_defer_flush()`
- `flush_tlb_batched_pending()`

Batched reclaim unmaps may defer TLB flushes to reduce IPIs. Dirty/writable cases force later flushes before I/O or freeing to avoid lost writes or data exposure. `mm->tlb_flush_batched` tracks pending/flushed generations.

## Address and PMD Helpers

- `page_address_in_vma()` computes the virtual address where a folio/page belongs in a VMA, validating anon root or file mapping identity.
- `mm_find_pmd()` walks PGD/P4D/PUD levels and returns the PMD pointer for an address if present.

## Referenced and Aging Logic

`folio_referenced()` walks reverse mappings to test and clear referenced/young state. It:

- Handles mlocked VMAs by restoring mlock state and reporting `VM_LOCKED`.
- Skips certain non-shared anonymous swapbacked folios in exiting/OOM-reaped address spaces.
- Batches PTE checks for large folios.
- Uses MGLRU look-around when enabled.
- Clears young bits via notifier-aware helpers.
- Filters VMAs without recency or outside target memcg.

It returns the number of referenced mappings or `-1` if rmap lock contention prevented a reliable walk.

## Dirty Cleaning and Write Protection

`page_vma_mkclean_one()` clears dirty and writable state from PTEs/PMDs with MMU notifier invalidation. It is used by:

- `folio_mkclean()`: clean shared mappings of a mapped folio.
- `mapping_wrprotect_range()`: write-protect all shared mappings for a mapping/pgoff/PFN range, including non-folio PFN mappings.
- `pfn_mkclean_range()`: clean/write-protect a PFN range within one VMA.

These paths are important for filesystem writeback and DAX-like mappings that need page-table dirty state synchronized to storage state.

## Mapcount and Rmap Accounting

`__folio_add_rmap()` and `__folio_remove_rmap()` implement shared accounting for PTE, PMD, and PUD mappings. They update:

- per-page mapcounts when enabled;
- large-folio mapcounts;
- entire-folio mapcounts for PMD/PUD mappings;
- `_nr_pages_mapped`;
- `NR_ANON_MAPPED`, `NR_FILE_MAPPED`, `NR_ANON_THPS`, `NR_FILE_PMDMAPPED`, and `NR_SHMEM_PMDMAPPED`.

Large folios, `CONFIG_NO_PAGE_MAPCOUNT`, and PMD-mapped THPs have specialized paths. Partial unmapping of anon large folios queues deferred split when appropriate.

Public add/remove wrappers include:

- `folio_add_anon_rmap_ptes()`
- `folio_add_anon_rmap_pmd()`
- `folio_add_new_anon_rmap()`
- `folio_add_file_rmap_ptes()`
- `folio_add_file_rmap_pmd()`
- `folio_add_file_rmap_pud()`
- `folio_remove_rmap_ptes()`
- `folio_remove_rmap_pmd()`
- `folio_remove_rmap_pud()`

`folio_move_anon_rmap()` moves an exclusive post-COW folio to the VMA's anon_vma.

## Try-To-Unmap

`try_to_unmap()` walks all mappings and calls `try_to_unmap_one()` to remove PTEs/hugetlb entries for reclaim, memory failure, or other unmap users.

`try_to_unmap_one()` handles:

- mlocked VMAs and restoration of missed mlock state;
- lazyfree folios and `MADV_FREE` discard behavior;
- optional THP PMD splitting;
- hugetlb poisoned-page unmapping and PMD sharing;
- present PTE clearing, optional batched TLB flushes, and dirty propagation;
- userfaultfd write-protect marker preservation;
- hwpoison entries;
- unused PTE discard;
- anonymous swap entry installation with soft-dirty, uffd-wp, and exclusive bits;
- arch-specific `arch_unmap_one()`;
- anon-exclusive sharing transitions before swap/migration exposure;
- file-backed RSS decrement and rmap removal.

The function is careful to restore PTEs and abort if swap duplication, architecture unmap, GUP/lazyfree checks, or anon-exclusive sharing fails.

## Migration

`try_to_migrate()` replaces mappings with migration entries through `try_to_migrate_one()`. It supports only specific `TTU_*` flags and skips unsupported zone-device folios. For anonymous migration it may ignore temporary stack VMAs used during exec because their VMA movement can race with page-table discovery.

`try_to_migrate_one()` parallels unmap logic but installs migration entries, preserving writable/readable/exclusive state, young/dirty, soft-dirty, and uffd-wp metadata. It supports PMD migration entries when `CONFIG_ARCH_ENABLE_THP_MIGRATION` is enabled and can split huge PMDs when requested.

## Device-Exclusive Mappings

Under `CONFIG_DEVICE_PRIVATE`, `make_device_exclusive()` converts a writable anonymous PTE into a device-exclusive PFN swap entry. It:

- Faults in and pins the target page writable.
- Requires anonymous non-hugetlb folios.
- Locks the folio.
- Issues an `MMU_NOTIFY_EXCLUSIVE` invalidation.
- Re-walks the VMA to verify the same writable PTE.
- Clears and flushes the PTE, marks dirty if needed, and installs a device-exclusive entry.
- Returns the page and locked folio to the caller.

This supports device memory managers that need exclusive device access coordinated with CPU faults.

## Rmap Walkers

`rmap_walk()` dispatches to KSM, anon, or file walkers:

- `rmap_walk_anon()` locks or uses a caller-held anon_vma lock, then iterates `anon_vma_interval_tree` entries overlapping the folio's pgoff range.
- `__rmap_walk_file()` iterates `mapping->i_mmap` over file VMAs for a specified pgoff range and supports non-folio PFN ranges.
- `rmap_walk_file()` wraps file-backed folio walking, relying on the folio lock to stabilize `folio->mapping`.
- `rmap_walk_locked()` is used when the relevant rmap lock is already held.

Each walker supports invalid-VMA filters, early stop callbacks, and contention signaling.

## Hugetlb Anonymous Rmap

When hugetlb is enabled:

- `hugetlb_add_anon_rmap()` increments entire and large mapcounts and handles exclusive state.
- `hugetlb_add_new_anon_rmap()` initializes mapcounts, clears restore-reserve state, sets anonymous mapping, and marks the page exclusive.

Hugetlb paths differ from normal anon pages because hugepages have separate accounting and no standard LRU behavior.

## Filesystem/MM Relevance

This is one of the core bridge files between filesystem page cache and virtual memory. Filesystems rely on it indirectly for page-cache dirty tracking, writeback preparation (`folio_mkclean()`), truncation/invalidation coordination, mmap write protection, reclaim unmapping, migration, and file-backed VMA traversal through `mapping->i_mmap`.
