# File Research: sources/os/linux/linux/fs/dax.c

## Summary
Implements Linux filesystem DAX helpers for direct access to persistent memory without page cache pages. It manages DAX entries in an address-space xarray, entry locking and waiting, DAX folio association/sharing, busy-page detection, invalidation, writeback, iomap read/write, zeroing, unsharing, mmap fault handling for PTE/PMD mappings, synchronous faults, dedupe comparison, and remap preparation.

## Main Responsibilities
- Encode DAX xarray value entries with flags for locked, PMD, zero-page, and empty states.
- Provide waitqueue-based locking and wakeup for DAX entries.
- Manage DAX folio mapping/index/share state and compound-order reset.
- Associate and disassociate DAX entries with address spaces and VMAs.
- Detect busy DAX pages before layout changes or truncation.
- Delete and invalidate DAX mapping entries and ranges.
- Break DAX layouts by unmapping and waiting for page idleness.
- Flush dirty DAX mappings for writeback/fsync.
- Translate iomap file offsets to DAX PFNs and kernel addresses.
- Copy around unaligned CoW writes and shared extents.
- Load zero pages for sparse holes.
- Unshare CoW ranges.
- Zero DAX ranges and truncate partial blocks.
- Implement `dax_iomap_rw()` for direct read/write.
- Handle DAX mmap faults through PTE and optional PMD paths.
- Finish synchronous MAP_SYNC faults after fsync.
- Compare DAX ranges for dedupe and prepare remap operations.

## Key APIs
- Entry/layout: `dax_lock_folio()`, `dax_unlock_folio()`, `dax_lock_mapping_entry()`, `dax_unlock_mapping_entry()`
- Busy/invalidation: `dax_layout_busy_page_range()`, `dax_layout_busy_page()`, `dax_delete_mapping_entry()`, `dax_delete_mapping_range()`, `dax_break_layout()`, `dax_break_layout_final()`, `dax_invalidate_mapping_entry_sync()`
- Writeback: `dax_writeback_mapping_range()`
- I/O and zeroing: `dax_file_unshare()`, `dax_zero_range()`, `dax_truncate_page()`, `dax_iomap_rw()`
- Faults: `dax_iomap_fault()`, `dax_finish_sync_fault()`
- Remap/dedupe: `dax_dedupe_file_range_compare()`, `dax_remap_file_range_prep()`
- Folio utility: `dax_folio_reset_order()`

## Important Behavior
DAX entries are xarray value entries, not page pointers. Four low bits encode lock, PMD size, zero page, and empty locking placeholder. PMD entries cover aligned PMD-sized index ranges; waitqueue keys align PMD indices so all offsets in a PMD range wait on the same lock.

`grab_mapping_entry()` favors existing PTE entries over PMD entries. A PMD zero or empty entry can be downgraded when a PTE is needed. Real PMD storage entries are left in place, and PTE writes dirty the whole PMD entry.

DAX folios represent device memory pages. Shared file mappings clear `folio->mapping` and use `folio->share`. `dax_folio_reset_order()` restores compound folios to order-0 state when sharing refs drop.

Writeback writeprotects mappings with `pfn_mkclean_range()`, flushes persistent memory with `dax_flush()`, and clears dirty tags only after cache flush and while fault insertion is serialized by entry locks.

Iomap read/write directly maps device ranges with `dax_direct_access()`. Reads from holes/unwritten extents zero the user iterator. Writes to new or shared extents invalidate mappings so mmap sees write(2) data. CoW paths copy head/tail data around unaligned writes to avoid stale bytes.

Fault handling uses locked DAX entries and iomap mappings. Read faults on holes insert zero pages; write faults allocate or map storage. Synchronous MAP_SYNC write faults can return a PFN and require caller completion through `dax_finish_sync_fault()` after fsync. PMD faults fall back when alignment, VMA bounds, COW, file size, or existing PTE entries prevent huge mappings.

## Research Notes
This file is highly synchronization-sensitive. Correctness depends on xarray entry locking, page table invalidation, DAX read locks, dirty/TOWRITE tags, iomap extent semantics, memory-failure/rmap expectations for DAX folios, and filesystem locks that prevent concurrent truncation or mapping changes during fault and layout operations.
