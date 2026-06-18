# File Research: sources/local-fs/btrfs-linux/fs/btrfs/subpage.c

This file implements subpage support for cases where Btrfs sectors or metadata nodes are smaller than the kernel folio/page size. It attaches a `btrfs_folio_state` to folios and tracks per-sector state bits for uptodate, dirty, writeback, ordered, checked, and locked ranges.

Context and limitations:
- The file documents current subpage constraints: 64K page-size focus, metadata read/write support, and metadata not crossing a 64K page boundary.
- Metadata reads can operate on only the target tree block inside a folio.
- Metadata writeback still works at full-folio granularity but submits only dirty extent buffers inside that folio.
- Metadata locking relies on `io_tree` locking rather than folio locking to avoid deadlocks and excessive serialization among multiple tree blocks in one page.

Folio private-state lifecycle:
- `btrfs_attach_folio_state()` attaches private state only when the folio is actually subpage for the requested metadata/data type and does nothing when private state already exists.
- `btrfs_detach_folio_state()` detaches and frees state only for matching subpage metadata/data cases.
- `btrfs_alloc_folio_state()` allocates a flexible bitmap large enough for all state lanes across `fsize / sectorsize` sectors, initializes the lock, and initializes either `eb_refs` for metadata or `nr_locked` for data.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata folio private state from being detached while extent buffers are being inserted or removed; callers must hold the mapping's `i_private_lock`.

Bitmap indexing and range handling:
- `btrfs_subpage_assert()` validates private state, sectorsize alignment, length alignment, and mapped-folio range containment.
- `subpage_calc_start_bit()` maps a byte range plus bitmap lane name to the starting bit in the packed bitmap.
- `btrfs_subpage_clamp_range()` intersects a caller range with the folio bounds and permits zero-length results for callers that walk folios beyond the logical target range.
- `subpage_test_bitmap_all_set()` and `subpage_test_bitmap_all_zero()` test whole-lane state for a folio.

Lock handling:
- `btrfs_subpage_end_and_test_lock()` clears the locked bits for a range, decrements `nr_locked`, and returns whether this was the final subpage lock.
- `btrfs_folio_end_lock()` handles non-subpage folios, plain `folio_lock()` cases with no subpage locked bits, and subpage range unlock cases.
- `btrfs_folio_end_lock_bitmap()` clears locked bits described by a sector bitmap and unlocks the folio only when all subpage locks are gone.
- `btrfs_folio_set_lock()` populates locked bits for a range on an already locked folio, mainly for async delalloc/compression paths that start from normal folio locking.

State operations:
- `btrfs_subpage_set_uptodate()` sets range bits and marks the whole folio uptodate only when all sectors are uptodate.
- `btrfs_subpage_clear_uptodate()` clears range bits and clears the folio uptodate flag.
- `btrfs_subpage_set_dirty()` sets range dirty bits and marks the folio dirty.
- `btrfs_subpage_clear_and_test_dirty()` clears range dirty bits and returns true when the folio has no dirty subpage sectors left.
- `btrfs_subpage_clear_dirty()` clears the folio dirty-for-IO state only when the last dirty subpage range was cleared.
- `btrfs_subpage_set_writeback()` sets range writeback bits and starts folio writeback; it preserves the writeback TOWRITE tag when the folio remains dirty so `WB_SYNC_ALL` does not miss it.
- `btrfs_subpage_clear_writeback()` clears range writeback bits and ends folio writeback when no writeback sectors remain.
- Ordered and checked helpers mirror this pattern, setting/clearing folio-level ordered/checked flags based on whole-lane state.

Generated helper families:
- `IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` creates all-set range tests for each bitmap lane.
- `IMPLEMENT_BTRFS_PAGE_OPS()` creates:
  - `btrfs_folio_set/clear/test_*()` for data folios that may or may not be subpage,
  - `btrfs_folio_clamp_set/clear/test_*()` for data folio operations where the requested range may exceed folio bounds,
  - `btrfs_meta_folio_set/clear/test_*()` for metadata extent-buffer ranges.
- Generated helpers fall back to normal folio operations when `fs_info` is absent in selftests or when the folio is not subpage.

Diagnostics and assertions:
- `btrfs_folio_assert_not_dirty()` asserts both folio dirty state and subpage dirty bits are clear, dumping the dirty bitmap on mismatch.
- `btrfs_subpage_dump_bitmap()` dumps all subpage bitmap lanes plus the base folio for debugging.
- `btrfs_get_subpage_dirty_bitmap()` reads the current dirty lane into a caller-supplied bitmap.
- `btrfs_meta_folio_clear_and_test_dirty()` clears metadata dirty state and returns whether the folio-level dirty flag was also cleared.

Cross-file relationships:
- `subpage.h` declares the bitmap layout, `btrfs_folio_state`, and all generated helper prototypes.
- Extent buffer and metadata I/O paths use the metadata helpers for tree blocks smaller than page size.
- Data writeback, compression, delalloc, and extent I/O paths use data folio and clamp helpers to bridge byte ranges to subpage sector state.
- `messages.h` provides warning output for bitmap dumps; `btrfs_inode.h` provides data-inode assertions used by the header.

Important invariants and risks:
- Subpage bitmap operations require an attached `btrfs_folio_state`; callers must attach private state before using subpage helpers.
- Start and length must be sectorsize-aligned.
- Metadata subpage currently assumes non-large folios.
- Folio-level flags summarize per-sector state but are deliberately conservative: uptodate/checked require all sectors, while dirty/writeback/ordered remain set while any sector is active.
- The locked bitmap and `nr_locked` allow one folio to represent multiple independently locked subranges; clearing the folio lock too early would break async delalloc and compression ordering.
- Writeback tag preservation in `btrfs_subpage_set_writeback()` is necessary for sync writeback correctness on dirty subpage folios.
