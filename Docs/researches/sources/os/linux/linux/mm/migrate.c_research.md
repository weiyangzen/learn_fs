# File Research: sources/os/linux/linux/mm/migrate.c

## Role

`migrate.c` is the core Linux folio/page migration implementation. It supplies common migration primitives used by compaction, memory hotplug/offlining, NUMA policy and balancing, memory failure handling, hugetlb migration, filesystem/page-cache migration callbacks, and userspace `move_pages(2)`.

## Main Responsibilities

- Registers and dispatches `movable_operations` for special movable pages such as offline balloon pages and zsmalloc pages.
- Isolates pages/folios from LRU, hugetlb lists, or movable-ops owners, and returns them via `putback_movable_pages()`.
- Converts mapped PTEs/PMDs to migration entries, waits on migration entries, and restores mappings with `remove_migration_ptes()`.
- Moves folio metadata and content from source to destination folios, including address-space xarray entries, swap cache state, dirty/writeback/accounting state, memcg ownership, KSM metadata, NUMA cpupid metadata, and page owner data.
- Implements batched and retrying migration loops through `migrate_pages()`.
- Implements `move_pages(2)` when `CONFIG_NUMA_MIGRATION` is enabled.
- Implements NUMA balancing migration helpers when `CONFIG_NUMA_BALANCING` is enabled.

## Key Entry Points

- `set_movable_ops()`: installs per-page-type movable callbacks for `PGTY_offline` and `PGTY_zsmalloc`.
- `isolate_movable_ops_page()`: pins, locks, callback-isolates, and marks a movable-ops page as isolated.
- `putback_movable_pages()`: generic cleanup for isolated LRU, hugetlb, and movable-ops pages.
- `remove_migration_ptes()`: walks reverse mappings and replaces migration entries with either the migrated destination page or the original source page.
- `migration_entry_wait()`, `migration_entry_wait_huge()`, `pmd_migration_entry_wait()`: fault-side wait helpers for PTE/hugetlb/PMD migration entries.
- `folio_migrate_mapping()`: atomically replaces a folio in its mapping or swap cache after refcount freezing.
- `folio_migrate_flags()`: transfers ancillary state after mapping replacement.
- `migrate_folio()`, `filemap_migrate_folio()`, `buffer_migrate_folio()`, `buffer_migrate_folio_norefs()`: exported migration callbacks for generic folios, page cache, and buffer-head users.
- `migrate_pages()`: public high-level migrator for lists of isolated folios.
- `alloc_migration_target()`: default destination allocation helper controlled by `struct migration_target_control`.
- `SYSCALL_DEFINE6(move_pages, ...)`: userspace NUMA page move/status syscall.
- `migrate_misplaced_folio_prepare()` and `migrate_misplaced_folio()`: NUMA fault migration helpers.

## Migration Pipeline

The ordinary non-hugetlb path is split into unmap and move phases:

1. `migrate_folio_unmap()` allocates a destination folio, locks source and destination, waits for writeback only when migration mode permits, obtains an `anon_vma` reference when needed, and installs migration PTEs via `try_to_migrate()`.
2. It records transient state in the destination folio private field: whether the source was mapped, whether it was mlocked, and the borrowed `anon_vma`.
3. `migrate_folio_move()` extracts that state, removes the destination from the temporary list, calls `move_to_new_folio()`, requeues deferred split state when needed, puts the destination on LRU, restores PTEs to destination, unlocks both folios, and drops migration references.
4. Failure paths call `migrate_folio_undo_src()` and `migrate_folio_undo_dst()` to restore migration PTEs, unlock folios, release destination allocation, and move failed folios to the caller’s return list unless retrying.

`migrate_pages_batch()` performs the same logic in batches for `MIGRATE_ASYNC`, first collecting unmapped folios and destination folios, then flushing TLBs once via `try_to_unmap_flush()`, then moving the batch. Synchronous migration first tries the async batch path and then falls back to one-by-one migration for failures.

## Mapping and Accounting Details

`__folio_migrate_mapping()` is the central atomic replacement routine. It freezes the source folio refcount at the expected value, unqueues deferred split state, copies index/mapping/swapcache/private state, moves dirty state, replaces xarray or swap-cache entries, unfreezes the source with the cache reference removed, and updates zone/lruvec counters when source and destination zones differ.

`folio_migrate_flags()` copies state that is not handled by mapping replacement: referenced, uptodate, active/unevictable, workingset, checked, mapped-to-disk, dirty fallback, young/idle, ref metadata, NUMA cpupid, KSM, swapcache clearing, private clearing, writeback waiter wakeup, readahead, owner metadata, allocation tags, and memcg migration.

## Special Page Classes

- Movable-ops pages are not ordinary LRU pages. Their owner callback handles isolate, putback, and migrate. The migration core still temporarily treats them as folios and locks/refcounts them.
- Hugetlb migration uses `unmap_and_move_huge_page()` with hugetlb-specific locking, rmap handling, and `move_hugetlb_state()`.
- THP/large folios may be migrated as large folios, split when migration is unsupported or allocation fails, or counted specially in migration statistics.
- Device-private pages can be restored through migration-entry handling in `remove_migration_pte()`, but device-specific collection/migration lives in `migrate_device.c`.

## Userspace and NUMA Interfaces

With `CONFIG_NUMA_MIGRATION`, `move_pages(2)` resolves user addresses to folios, validates target nodes against cpuset and memory-node availability, enforces `MPOL_MF_MOVE_ALL` privilege, isolates eligible folios, migrates by target node batches, and writes per-page status back to userspace.

With `CONFIG_NUMA_BALANCING`, misplaced folio migration avoids dirty file folios, shared executable mappings, and target nodes below watermarks. Tiering mode can wake kswapd and tracks promotion success in lruvec stats.

## Concurrency and Failure Model

This file is heavily built around refcount freezing, folio locks, rmap locks, page-table locks, xarray/swap-cluster locks, mmap/rmap coordination, and TLB flush batching. Retryable failures generally use `-EAGAIN`; permanent failures move folios to return lists; low-memory allocation failure can short-circuit the batch with `-ENOMEM`. The caller must put back remaining isolated folios when `migrate_pages()` reports nonzero/negative results.

## Filesystem Relevance

Filesystem address spaces participate through `address_space_operations::migrate_folio`. If a filesystem does not provide a callback, `fallback_migrate_folio()` refuses dirty folios and requires private data release before using generic migration. Buffer-head filesystems can use `buffer_migrate_folio()` when buffer references are controlled by the folio lock, or `buffer_migrate_folio_norefs()` when direct buffer-head references must be checked.
