# File Research: sources/os/linux/linux/mm/filemap.c

## Purpose

This is the central generic Linux page-cache implementation for normal files. It handles page-cache insertion/removal, folio lookup, writeback coordination, read paths, splice reads, mmap faults and fault-around, direct/buffered write integration, folio lifecycle helpers, cache invalidation, and optional `cachestat(2)` support.

## Major Responsibilities

- Maintain `address_space->i_pages` xarray entries for cached folios, shadow entries, swap/shmem entries, and DAX-like value entries.
- Provide generic read and write operations used by many filesystems.
- Coordinate dirty/writeback state and error reporting.
- Implement folio wait queues and folio lock/writeback wakeups.
- Support large folios and PMD mapping where allowed.
- Protect truncate/hole-punch races using `mapping->invalidate_lock`.
- Provide mmap fault handling for file-backed VMAs.

## Page Cache Removal and Accounting

Key helpers:

- `page_cache_delete()`: removes one locked folio from the xarray, clears marks, detaches mapping, and subtracts `nrpages`.
- `filemap_unaccount_folio()`: verifies folio is unmapped, updates LRU/node/memcg stats, handles THP/shmem/kernel-file accounting, and cleans dirty accounting if necessary.
- `__filemap_remove_folio()`: trace + unaccount + delete.
- `filemap_remove_folio()`: public locked-folio removal with inode lock and xarray lock.
- `delete_from_page_cache_batch()`: batch removal optimized for sorted dense folio batches.
- `filemap_free_folio()`: calls filesystem `free_folio()` then drops page-cache references.

## Writeback and Error Handling

Important exported functions:

- `filemap_check_errors()`
- `filemap_fdatawrite_range()`
- `filemap_fdatawrite()`
- `filemap_flush_range()`
- `filemap_flush()`
- `filemap_flush_nr()`
- `filemap_fdatawait_range()`
- `filemap_fdatawait_range_keep_errors()`
- `file_fdatawait_range()`
- `filemap_write_and_wait_range()`
- `file_write_and_wait_range()`
- `file_check_and_advance_wb_err()`
- `__filemap_set_wb_err()`

The file uses `mapping->wb_err` / `file->f_wb_err` errseq tracking so writeback errors can be reported once per file descriptor, especially through fsync-like paths. Legacy `AS_EIO` and `AS_ENOSPC` bits are also checked and cleared or preserved depending on helper.

## Page Cache Insertion and Replacement

Key helpers:

- `replace_page_cache_folio()`: atomically replaces an old locked folio with a new locked folio in the page cache.
- `__filemap_add_folio()`: low-level insertion into xarray, handling conflicts, shadow entries, large-entry splitting, accounting, and reference setup.
- `filemap_add_folio()`: charges memcg, locks folio, inserts, handles workingset refault, adds to LRU, and kernel-file stats.
- NUMA-aware `filemap_alloc_folio_noprof()` supports mempolicy and cpuset memory spreading.

Important invariants:

- Inserted folios must be locked.
- Folio index must align to folio size.
- Folio order must satisfy mapping minimum order.
- Large xarray value conflicts may be split to fit smaller folios.
- Shadow entries can be returned to callers for workingset refault logic.

## Invalidation Lock Helpers

- `filemap_invalidate_lock_two()` and `filemap_invalidate_unlock_two()` lock two mappings in address order to avoid deadlock.
- Read and write paths use shared/exclusive invalidate locks to synchronize with truncate and hole punching.

## Folio Wait Queues and Locking

The file defines hashed wait queues:

- `folio_wait_table[256]`
- `folio_waitqueue(folio)`

`pagecache_init()` initializes wait queues, writeback, and sysctl `vm/page_lock_unfairness`.

Core wait/wakeup functions:

- `wake_page_function()`
- `folio_wake_bit()`
- `folio_wait_bit_common()`
- `folio_wait_bit()`
- `folio_wait_bit_killable()`
- `folio_unlock()`
- `folio_end_read()`
- `folio_end_writeback_no_dropbehind()`
- `folio_end_writeback()`
- `__folio_lock()`
- `__folio_lock_killable()`
- `__folio_lock_or_retry()`

The lock wait logic supports shared waits, exclusive waits, dropped-reference waits, and fair lock handoff after configurable unfairness. It also accounts thrashing stalls for non-uptodate workingset folios.

## Lookup and Batch Traversal

Core lookup:

- `filemap_get_entry()`: lockless RCU lookup with speculative folio refcounting.
- `__filemap_get_folio_mpol()`: lookup/create API with `FGP_*` flags, locking, accessed/stable handling, large folio allocation, and NOWAIT behavior.

Batch APIs:

- `find_get_entries()`
- `find_lock_entries()`
- `filemap_get_folios()`
- `filemap_get_folios_contig()`
- `filemap_get_folios_tag()`
- `filemap_get_folios_dirty()`

Gap APIs:

- `page_cache_next_miss()`
- `page_cache_prev_miss()`

These rely on xarray RCU traversal and carefully pin folios only after checking they remain in the xarray.

## Generic Buffered Read Path

Primary functions:

- `filemap_get_read_batch()`
- `filemap_read_folio()`
- `filemap_range_uptodate()`
- `filemap_update_page()`
- `filemap_create_folio()`
- `filemap_readahead()`
- `filemap_get_pages()`
- `filemap_read()`
- `generic_file_read_iter()`

Flow:

1. `generic_file_read_iter()` handles direct I/O first if `IOCB_DIRECT` is set.
2. Short direct reads may fall back to buffered reads unless DAX or complete/error.
3. `filemap_read()` gets batches of cached folios, drives readahead or synchronous `read_folio`, checks i_size after folios become uptodate, flushes dcache for writable mappings, and copies to the iterator.
4. `IOCB_NOWAIT`, `IOCB_NOIO`, `IOCB_WAITQ`, and `IOCB_DONTCACHE` alter blocking, I/O submission, async wait, and dropbehind behavior.

## Dropbehind / Uncached Reads and Writes

The file supports `FGP_DONTCACHE` and `IOCB_DONTCACHE` through folio `dropbehind` marking. Clean non-writeback dropbehind folios can be invalidated after reads or writeback completion. Dirty dropbehind accounting is adjusted when a non-uncached lookup clears the flag.

## Direct I/O and Buffered Write Integration

Key functions:

- `kiocb_write_and_wait()`
- `filemap_invalidate_pages()`
- `kiocb_invalidate_pages()`
- `kiocb_invalidate_post_direct_write()`
- `generic_file_direct_write()`
- `generic_perform_write()`
- `__generic_file_write_iter()`
- `generic_file_write_iter()`

Behavior:

- Direct writes first write back and invalidate overlapping cache unless NOWAIT requires `-EAGAIN`.
- After direct write, clean cached pages are invalidated again to reduce stale-cache risk.
- Failure to invalidate page cache after direct I/O logs a ratelimited critical warning and sets writeback error.
- Buffered writes loop over `write_begin` / copy / `write_end`, throttle dirty pages, handle short copies, shrink chunk size for large folios on zero progress, and fault in user pages outside filesystem locks for progress.
- `generic_file_write_iter()` wraps checks, inode locking, and sync-on-write handling.

## Splice and SEEK_HOLE / SEEK_DATA

Splice helpers:

- `splice_folio_into_pipe()`
- `filemap_splice_read()`

They move page-cache folio references into pipe buffers, using page-cache pipe buffer operations.

Seek helpers:

- `mapping_seek_hole_data()`
- `folio_seek_hole_data()`
- `seek_folio_size()`

The seek implementation can use `is_partially_uptodate()` to distinguish block-level holes/data inside non-uptodate folios.

## mmap Fault Handling

Under `CONFIG_MMU`, key functions:

- `filemap_fault()`
- `filemap_map_pages()`
- `filemap_page_mkwrite()`
- `generic_file_mmap()`
- `generic_file_mmap_prepare()`
- `generic_file_readonly_mmap()`
- `generic_file_readonly_mmap_prepare()`

Fault flow:

1. Rejects faults beyond i_size with `VM_FAULT_SIGBUS`.
2. Attempts page-cache lookup.
3. Existing folio may trigger async mmap readahead.
4. Missing folio triggers major fault accounting and sync mmap readahead.
5. Uses `invalidate_lock` before creating or reading folios to synchronize with truncate/hole punch.
6. Locks folio, potentially dropping mmap/per-VMA lock and returning `VM_FAULT_RETRY`.
7. Reads non-uptodate folios synchronously.
8. Rechecks i_size under folio lock.
9. Returns locked page via `vmf->page`.

Readahead helpers:

- `do_sync_mmap_readahead()`
- `do_async_mmap_readahead()`

They respect `VM_RAND_READ`, `VM_SEQ_READ`, `VM_EXEC`, THP/PMD folio constraints, and `ra->mmap_miss`.

Fault-around mapping:

- `filemap_map_pmd()` attempts PMD mapping of large folios.
- `next_uptodate_folio()` finds lockable uptodate folios.
- `filemap_map_folio_range()` maps ranges of large folios into PTEs.
- `filemap_map_order0_folio()` handles order-0 folios.
- `filemap_map_pages()` maps multiple cached folios around a fault and updates RSS counters.

Non-MMU builds return `-ENOSYS` for mmap helpers and `VM_FAULT_SIGBUS` for page_mkwrite.

## Read Cache Helpers

- `read_cache_folio()`
- `mapping_read_folio_gfp()`
- `read_cache_page()`
- `read_cache_page_gfp()`

These get or create a cache folio/page, invoke a filler or `read_folio`, wait for uptodate state, and return pinned folio/page. They expect `mapping->invalidate_lock` to be held.

## Folio Release and Inode Invalidation

- `filemap_release_folio()` releases filesystem-private folio metadata using `a_ops->release_folio()` or `try_to_free_buffers()`, but refuses writeback folios.
- `filemap_invalidate_inode()` optionally writes back, unmaps, invalidates page cache over a byte range, and checks writeback errors.

## cachestat Support

Under `CONFIG_CACHESTAT_SYSCALL`:

- `filemap_cachestat()` walks xarray entries and counts cached, dirty, writeback, evicted, and recently evicted pages.
- It handles shadow entries and shmem swap entries.
- `can_do_cachestat()` restricts cache-status visibility to writable/openable/owner-capable users.
- `SYSCALL_DEFINE4(cachestat, ...)` validates fd, user pointers, flags, hugetlb exclusion, permissions, and returns `struct cachestat`.

## Key External Dependencies

This file is deeply integrated with:

- xarray / maple-like page cache storage
- folios and large folios
- writeback and errseq
- readahead
- memcg and lruvec stats
- VFS inode/file operations
- direct I/O
- VM fault machinery
- swap/shmem and workingset tracking
- pipe/splice infrastructure
- sysctl and optional cachestat syscall

## High-Risk Areas

- Lock ordering is explicitly documented at the top and is essential: `i_rwsem`, `invalidate_lock`, `mmap_lock`, `i_mmap_rwsem`, page-table locks, `i_pages`, LRU locks, and writeback locks interact.
- Lockless xarray lookup relies on RCU plus speculative refcounting and reload checks.
- mmap fault retry paths must correctly manage dropped mmap locks and pinned files.
- Direct I/O invalidation failure is treated as possible data corruption.
- Large folio and PMD mapping paths must preserve SIGBUS semantics beyond i_size.
