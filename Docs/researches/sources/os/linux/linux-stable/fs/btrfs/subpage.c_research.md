# File Research: sources/os/linux/linux-stable/fs/btrfs/subpage.c

This file implements Btrfs subpage folio state handling for cases where filesystem sector size or metadata node size is smaller than the kernel folio/page size.

Purpose:
- Tracks per-sector state inside a folio using `struct btrfs_folio_state`.
- Supports separate bitmap state for uptodate, dirty, writeback, ordered, checked, and locked sectors.
- Bridges normal folio-level flags with subpage-aware operations.

Folio state lifecycle:
- `btrfs_attach_folio_state()` attaches subpage private state only when needed:
  - metadata requires subpage support when nodesize is smaller than `PAGE_SIZE`,
  - data requires subpage support when sectorsize is smaller than folio size.
- `btrfs_detach_folio_state()` detaches and frees the private state when the folio no longer needs it.
- `btrfs_alloc_folio_state()` sizes the bitmap array as `btrfs_bitmap_nr_max * sectors_per_folio`, initializes the spinlock, and initializes either metadata `eb_refs` or data `nr_locked`.

Metadata extent-buffer references:
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect subpage metadata folio state from being detached while extent buffers are being created or destroyed.
- These helpers require the mapping private lock and only operate when metadata subpage mode is active.

Range validation and clamping:
- `btrfs_subpage_assert()` verifies private state exists, start/length are sector-aligned, and mapped folio ranges fit within the folio.
- `subpage_calc_start_bit()` maps a byte range and bitmap kind to a starting bit offset.
- `btrfs_subpage_clamp_range()` safely truncates arbitrary data ranges to the portion covered by the current folio.

Lock handling:
- `btrfs_folio_set_lock()` marks per-sector locked bits for a range already protected by the ordinary folio lock.
- `btrfs_folio_end_lock()` clears subpage lock bits and unlocks the folio only when the last subpage lock is gone.
- `btrfs_folio_end_lock_bitmap()` clears locked bits from a caller-provided bitmap.
- The implementation handles folios locked by plain `folio_lock()` with no subpage lock bits by simply unlocking the folio.

Bitmap operations:
- Direct subpage setters/clearers/testers are implemented for:
  - uptodate,
  - dirty,
  - writeback,
  - ordered,
  - checked.
- Uptodate and checked mark the whole folio flag only when all subpage bits are set.
- Clearing uptodate or checked clears the whole folio flag.
- Dirty marking sets subpage dirty bits and marks the folio dirty.
- `btrfs_subpage_clear_and_test_dirty()` returns whether clearing a range made the full dirty bitmap empty.
- Writeback handling starts folio writeback only when needed and ends folio writeback when all subpage writeback bits are clear.
- `btrfs_subpage_set_writeback()` preserves writeback indexing semantics for still-dirty folios so `WB_SYNC_ALL` writeback does not miss remaining dirty data.

Macro-generated API families:
- `IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` generates direct subpage test functions.
- `IMPLEMENT_BTRFS_PAGE_OPS()` generates:
  - `btrfs_folio_set_*`,
  - `btrfs_folio_clear_*`,
  - `btrfs_folio_test_*`,
  - clamped data-folio variants,
  - metadata extent-buffer variants.
- Non-subpage and selftest paths fall back to ordinary folio flag operations.

Assertions and diagnostics:
- `btrfs_folio_assert_not_dirty()` checks both folio dirty state and subpage dirty bitmap state under `CONFIG_BTRFS_ASSERT`.
- `btrfs_subpage_dump_bitmap()` dumps all subpage bitmaps for a folio and includes `dump_page()` output.
- `btrfs_get_subpage_dirty_bitmap()` exports the dirty bitmap for callers that need to submit or inspect dirty subranges.

Concurrency:
- Per-folio bitmap operations are protected by `btrfs_folio_state.lock`.
- `nr_locked` is atomic because multiple subpage lock ranges can coexist.
- Metadata `eb_refs` is atomic but must be manipulated under the mapping private lock.
