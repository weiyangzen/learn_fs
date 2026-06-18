# File Research: sources/os/linux/linux/mm/truncate.c

## Purpose
Implements page-cache truncation and invalidation for address spaces. It removes folios and exceptional entries, handles partial folios on truncate/hole-punch, supports stronger invalidation for direct I/O and filesystem coherency, and updates page cache when file size changes.

## Main Interfaces
- Exceptional cleanup: `clear_shadow_entries()`, `truncate_folio_batch_exceptionals()`.
- Folio invalidation/removal: `folio_invalidate()`, `truncate_inode_folio()`, `truncate_inode_partial_folio()`, `mapping_evict_folio()`, `folio_unmap_invalidate()`.
- Truncation: `truncate_inode_pages_range()`, `truncate_inode_pages()`, `truncate_inode_pages_final()`.
- Invalidation: `mapping_try_invalidate()`, `invalidate_mapping_pages()`, `invalidate_inode_pages2_range()`, `invalidate_inode_pages2()`.
- Page-cache size helpers: `truncate_pagecache()`, `truncate_setsize()`, `pagecache_isize_extended()`, `truncate_pagecache_range()`.
- Memory failure helper: `generic_error_remove_folio()`.

## Control Flow
Range truncation first removes fully covered locked folios in a nonblocking pass, processes partial start/end folios by zeroing invalidated ranges and splitting large folios when necessary, then performs a second pass that waits on writeback and removes remaining folios. Exceptional XArray entries are cleared except for shmem-managed entries and DAX-specific handling.

Partial folios are zeroed where accessible, invalidated through filesystem callbacks if needed, and split at truncation boundaries to preserve SIGBUS and hole semantics. If splitting fails, non-shmem mappings are unmapped so future faults occur at PTE granularity.

Invalidate paths differ by strength. `invalidate_mapping_pages()` removes clean, unlocked, evictable folios and shadow entries without blocking on I/O. `invalidate_inode_pages2_range()` unmaps mapped folios, waits for writeback, launders dirty folios through filesystem callbacks, releases private data, and returns `-EBUSY` if invalidation cannot complete.

File-size helpers unmap and truncate pagecache before filesystem block release, handle extension over sub-page block boundaries by write-protecting/dirtying the straddling folio, and zero newly exposed post-EOF ranges.

## State And Synchronization
Uses the mapping XArray, folio locks, inode `i_lock`, `mapping->i_pages` xarray lock, writeback waits, and filesystem `a_ops` callbacks. Final truncation marks the mapping exiting and cycles the XArray lock to avoid reclaim installing eviction state during inode teardown.

## Dependencies
Depends on filemap, folio batches, workingset shadow updates, shmem and DAX special cases, rmap unmapping, filesystem address-space operations, inode LRU shrinkability, and page-cache size management.

## Risks And Review Focus
- Large folio splitting and unmapping around partial truncation is subtle and affects SIGBUS/hole-punch semantics.
- DAX exceptional entries require filesystem coordination before truncation.
- Strong invalidation intentionally ignores transient references but must not remove dirty/private folios unsafely.
- `truncate_pagecache()` performs a second unmap for correctness with private COW pages racing truncation.
