# File Research: sources/local-fs/btrfs-linux/fs/btrfs/subpage.h

This header defines Btrfs subpage folio state and declares the helper API used by data and metadata paths when filesystem sectors or metadata nodes are smaller than the kernel folio size.

Bitmap layout:
- Packed bitmap lanes are ordered by lowercase enum values because macros use those names to generate function names.
- Lanes are:
  - `uptodate`,
  - `dirty`,
  - `writeback`,
  - `ordered`,
  - `checked`,
  - `locked`,
  - `max`.
- Each lane contains one bit per sector inside the folio.
- Comments note that ordered and checked are deprecated COW-fixup flags and that locked/writeback behavior is tied to async delalloc/compression lifecycle constraints.

`struct btrfs_folio_state`:
- Attached to `folio->private` for both data and metadata inodes when subpage state is needed.
- Contains a spinlock protecting bitmap lanes.
- Uses a union:
  - metadata uses `atomic_t eb_refs` to prevent premature detach while extent buffers refer to the folio,
  - data uses `atomic_t nr_locked` to count locked sectors inside the folio.
- Ends with a flexible `unsigned long bitmaps[]` sized by `btrfs_alloc_folio_state()`.

Subpage detection:
- `btrfs_meta_is_subpage()` returns true when `nodesize < PAGE_SIZE`; this works for metadata even for dummy extent-buffer folios without mappings.
- `btrfs_is_subpage()` returns true when `fs_info->sectorsize < folio_size(folio)` and asserts mapped folios belong to data inodes.

Lifecycle API:
- `btrfs_attach_folio_state()` and `btrfs_detach_folio_state()` manage folio private state.
- `btrfs_alloc_folio_state()` and `btrfs_free_folio_state()` allocate/free the private state.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` manage metadata extent-buffer references.

Lock API:
- `btrfs_folio_end_lock()` ends a byte-range subpage lock and unlocks the folio only when all subpage locks are gone.
- `btrfs_folio_set_lock()` marks a range locked on an already locked folio.
- `btrfs_folio_end_lock_bitmap()` clears locked sectors from a caller-provided bitmap.

Generated state APIs:
- `DECLARE_BTRFS_SUBPAGE_OPS(name)` declares subpage, data-folio, clamped-data-folio, and metadata-folio helpers for each state lane.
- The header declares full helper families for `uptodate`, `dirty`, `writeback`, `ordered`, and `checked`.
- Data helpers expect ranges inside one folio unless using the `clamp` variants.
- Metadata helpers use extent-buffer start/length and have no clamp variants because metadata folios are either subpage nodesize ranges or ordinary folios.

Other helpers:
- `btrfs_folio_clamp_finish_io()` is an error-cleanup helper that clears dirty, starts writeback, then clears writeback for a clamped range.
- `btrfs_subpage_clear_and_test_dirty()` clears dirty bits and reports whether this was the last dirty range.
- `btrfs_folio_assert_not_dirty()` verifies folio and subpage dirty state.
- `btrfs_meta_folio_clear_and_test_dirty()` handles metadata dirty clearing.
- `btrfs_get_subpage_dirty_bitmap()` exposes dirty-sector bitmap state to callers.
- `btrfs_subpage_dump_bitmap()` is a cold diagnostic dump helper.

Cross-file relationships:
- Implemented by `subpage.c`.
- Used by extent I/O, metadata extent-buffer, writeback, delalloc, and compression paths that cannot rely solely on folio-level flags.
- Includes `btrfs_inode.h` for `is_data_inode()` assertions in `btrfs_is_subpage()`.

Important invariants:
- Subpage metadata detection depends on nodesize, not mapping, because dummy extent-buffer folios can be unmapped.
- The bitmap lane order is part of the macro-generated ABI inside this translation unit pair.
- Per-sector state must remain synchronized with folio-level summary flags to preserve page-cache and writeback semantics.
