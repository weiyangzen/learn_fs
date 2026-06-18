# File Research: sources/os/linux/linux/fs/btrfs/subpage.c

## Scope And Role

`subpage.c` implements Btrfs support for filesystems whose sector size is smaller than the memory folio size. In that mode a single folio can contain multiple filesystem sectors or multiple metadata tree blocks, so normal folio flags are too coarse.

The file attaches a `struct btrfs_folio_state` to folios and maintains per-sector bitmaps for:

- Uptodate.
- Dirty.
- Writeback.
- Ordered.
- Checked.
- Locked.

The helpers provide both strict subpage operations and wrapper operations that fall back to normal folio flags on non-subpage filesystems.

## Design Overview

The opening comment describes subpage constraints and behavior:

- Historically focused on 64 KiB page size.
- Metadata read supports subpage granularity.
- Metadata writeback can still operate at folio scope but submits dirty extent buffers inside the folio.
- Metadata cannot rely solely on folio locking because multiple tree blocks may share one folio; it relies on io-tree locking for concurrency.
- Both data and metadata use `btrfs_folio_state` to track per-sector state.

## Folio State Allocation And Lifetime

`btrfs_attach_folio_state()` attaches private subpage state when needed. It skips attachment if:

- The folio already has private data.
- Metadata is not subpage.
- Data does not have sector size smaller than folio size.

For metadata it asserts the folio is not large. For mapped folios it asserts the folio is locked.

`btrfs_detach_folio_state()` detaches and frees the state if the folio is private and the requested folio type is actually subpage.

`btrfs_alloc_folio_state()` allocates enough bitmap storage for `btrfs_bitmap_nr_max * blocks_per_folio`, initializes the spinlock, and initializes either:

- `eb_refs` for metadata.
- `nr_locked` for data.

`btrfs_free_folio_state()` is an inline free in the header.

## Metadata Extent-Buffer References

`btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata folio state lifetime during extent-buffer allocation/free races.

They operate only when metadata is subpage and require `folio->mapping->i_private_lock`. The counter prevents detaching folio private state while an extent buffer sharing the folio is still being created or torn down.

## Range Validation And Bitmap Layout

`btrfs_subpage_assert()` verifies:

- Folio private state exists.
- `start` and `len` are sector-aligned.
- For mapped folios, the range lies inside the folio.

`subpage_calc_start_bit()` computes the starting bit for a named bitmap by combining:

- Sector offset inside the folio.
- Bitmap number multiplied by blocks per folio.

`btrfs_subpage_clamp_range()` truncates an arbitrary range to the portion inside a folio. If the folio is outside the range, it sets length to zero so callers can safely no-op.

`subpage_test_bitmap_all_set()` and `subpage_test_bitmap_all_zero()` test full-bitmap state for deciding when the coarse folio flag can be set or cleared.

## Subpage Lock Tracking

`btrfs_folio_set_lock()` records subpage-locked sectors inside a folio that was already locked by regular folio locking. It asserts the target bits were clear, sets locked bits, and increments `nr_locked`.

`btrfs_folio_end_lock()` releases subpage locks for a range and unlocks the folio only when the last subpage lock is cleared. It falls back to `folio_unlock()` for non-subpage folios or plain-locked subpage folios with `nr_locked == 0`.

`btrfs_folio_end_lock_bitmap()` clears locked sectors from a caller-provided bitmap and unlocks when the last tracked subpage lock is gone.

`btrfs_subpage_end_and_test_lock()` is the internal locked-bitmap clearing helper. It handles special compression/writeback paths where the folio was locked without subpage locked bits.

## Per-State Operations

Manual implementations handle flags whose coarse folio semantics need special care.

`btrfs_subpage_set_uptodate()` sets range bits and marks the whole folio uptodate only when all sectors are uptodate.

`btrfs_subpage_clear_uptodate()` clears range bits and clears the folio uptodate flag unconditionally.

`btrfs_subpage_set_dirty()` sets dirty bits and marks the folio dirty.

`btrfs_subpage_clear_and_test_dirty()` clears dirty bits and returns true if no dirty bits remain. Callers must clear the folio dirty flag themselves when appropriate.

`btrfs_subpage_clear_dirty()` clears dirty bits and clears the folio dirty-for-IO flag when the last dirty bit is gone.

`btrfs_subpage_set_writeback()` sets writeback bits and starts folio writeback if needed. It preserves the TOWRITE tag when the folio remains dirty so `WB_SYNC_ALL` does not miss still-dirty folios.

`btrfs_subpage_clear_writeback()` clears writeback bits and ends folio writeback when all writeback bits are gone.

`btrfs_subpage_set_ordered()` and `btrfs_subpage_clear_ordered()` maintain ordered bits and the coarse ordered folio flag.

`btrfs_subpage_set_checked()` marks the folio checked only when all checked bits are set.

`btrfs_subpage_clear_checked()` clears checked bits and clears the coarse checked flag.

`IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` generates range test helpers for uptodate, dirty, writeback, ordered, and checked.

## Folio Wrapper Operations

`IMPLEMENT_BTRFS_PAGE_OPS()` generates a full family of helpers for each state:

- `btrfs_folio_set_*`
- `btrfs_folio_clear_*`
- `btrfs_folio_test_*`
- `btrfs_folio_clamp_set_*`
- `btrfs_folio_clamp_clear_*`
- `btrfs_folio_clamp_test_*`
- `btrfs_meta_folio_set_*`
- `btrfs_meta_folio_clear_*`
- `btrfs_meta_folio_test_*`

These wrappers use normal folio operations when there is no `fs_info` or when the folio is not subpage, which also supports existing selftests that pass minimal filesystem state.

For metadata helpers, the range is derived from the `extent_buffer` start and length.

## Dirty Assertions And Metadata Dirty Clearing

`btrfs_folio_assert_not_dirty()` is active under `CONFIG_BTRFS_ASSERT`. It checks both the coarse folio dirty flag and the subpage dirty bits, dumping dirty bitmaps when an unexpected dirty range is found.

`btrfs_meta_folio_clear_and_test_dirty()` clears metadata dirty bits for an extent buffer and clears the folio dirty-for-IO flag when the last dirty subpage range is gone. Non-subpage metadata clears the folio directly and returns true.

## Bitmap Debugging And Export

`GET_SUBPAGE_BITMAP()` reads one named bitmap into an `unsigned long`.

`SUBPAGE_DUMP_BITMAP()` logs one named bitmap.

`btrfs_subpage_dump_bitmap()` dumps all subpage bitmaps plus the underlying page for debugging.

`btrfs_get_subpage_dirty_bitmap()` exports the dirty bitmap for callers that need to inspect dirty sectors.

## Concurrency And Locking

`btrfs_folio_state->lock` protects bitmap mutation and reads. Many operations use `spin_lock_irqsave()` because they may interact with writeback or completion contexts.

`nr_locked` is atomic but still updated under the bitmap lock when tied to bitmap changes.

Metadata `eb_refs` is atomic and additionally protected by `i_private_lock` at call sites to coordinate folio-private lifetime.

Folio coarse flags are updated only when subpage bitmap state reaches all-set or all-zero thresholds.

## Integration Points

This file is used by extent I/O, metadata extent-buffer handling, delalloc/writeback paths, compression paths, and COW fixup/ordered extent state management. The public declarations live in `subpage.h`.

It depends on folio APIs, bitmap APIs, Btrfs inode helpers, extent-buffer metadata, and filesystem sector-size fields.

## Risks And Edge Cases

Zero-length clamped ranges are intentionally accepted by subpage helpers.

Subpage state must be attached before bitmap helpers run; assertions catch missing private state.

Misbalanced subpage lock setting/ending can leave a folio locked or unlock it too early. The code asserts `nr_locked` bounds against cleared bits.

Dirty/writeback interactions are subtle because folio-level dirty and writeback flags aggregate multiple sector bits.

The generated wrapper functions rely on correct `btrfs_is_subpage()` and `btrfs_meta_is_subpage()` decisions.

## Testing Signals

Useful tests should cover:

- Sector-sized dirty/uptodate/writeback/ordered/checked transitions inside one folio.
- Coarse folio flag transitions when all bits become set or clear.
- Subpage lock reference counting with overlapping ranges and bitmap unlock.
- Metadata folios with multiple extent buffers.
- Dirty assertion failure diagnostics.
- Clamp helpers for ranges partially or wholly outside a folio.
- Non-subpage fallback behavior.
