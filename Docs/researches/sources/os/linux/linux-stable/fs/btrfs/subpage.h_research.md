# File Research: sources/os/linux/linux-stable/fs/btrfs/subpage.h

This header declares Btrfs subpage support types and helper APIs.

Core concept:
- When Btrfs sector size or metadata node size is smaller than a folio, a single folio can contain multiple independently tracked Btrfs sectors or tree blocks.
- `struct btrfs_folio_state` stores per-sector bitmaps in `folio->private`.

Bitmap layout:
- `btrfs_bitmap_nr_uptodate`,
- `btrfs_bitmap_nr_dirty`,
- `btrfs_bitmap_nr_writeback`,
- `btrfs_bitmap_nr_ordered`,
- `btrfs_bitmap_nr_checked`,
- `btrfs_bitmap_nr_locked`,
- `btrfs_bitmap_nr_max`.

State object:
- `struct btrfs_folio_state` contains:
  - `lock` for bitmap protection,
  - metadata-only `eb_refs`,
  - data-only `nr_locked`,
  - flexible bitmap storage.
- `enum btrfs_folio_type` distinguishes metadata and data users.

Subpage detection:
- `btrfs_meta_is_subpage()` returns true when `nodesize < PAGE_SIZE`.
- `btrfs_is_subpage()` returns true when `sectorsize < folio_size(folio)` and asserts mapped folios belong to data inodes.

Declared lifecycle APIs:
- `btrfs_attach_folio_state()`,
- `btrfs_detach_folio_state()`,
- `btrfs_alloc_folio_state()`,
- `btrfs_free_folio_state()`.

Metadata extent-buffer reference APIs:
- `btrfs_folio_inc_eb_refs()`,
- `btrfs_folio_dec_eb_refs()`.

Lock APIs:
- `btrfs_folio_end_lock()`,
- `btrfs_folio_set_lock()`,
- `btrfs_folio_end_lock_bitmap()`.

Generated bitmap operation declarations:
- `DECLARE_BTRFS_SUBPAGE_OPS(name)` declares subpage, folio, clamped folio, and metadata folio variants.
- Operations are declared for:
  - uptodate,
  - dirty,
  - writeback,
  - ordered,
  - checked.

Additional helpers:
- `btrfs_folio_clamp_finish_io()` clears dirty, sets writeback, then clears writeback for error cleanup.
- `btrfs_subpage_clear_and_test_dirty()` clears dirty bits and reports whether the whole folio is now clean.
- `btrfs_folio_assert_not_dirty()` verifies folio and bitmap cleanliness.
- `btrfs_meta_folio_clear_and_test_dirty()` is the metadata extent-buffer dirty-clear helper.
- `btrfs_get_subpage_dirty_bitmap()` retrieves dirty bitmap state.
- `btrfs_subpage_dump_bitmap()` provides cold-path diagnostics.

Design notes:
- The header explicitly separates direct subpage helpers from folio helpers and clamped data-folio helpers.
- Metadata callers are expected to use `btrfs_meta_folio_*()` helpers rather than clamp variants.
