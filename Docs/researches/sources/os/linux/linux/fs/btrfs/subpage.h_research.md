# File Research: sources/os/linux/linux/fs/btrfs/subpage.h

## Scope And Role

`subpage.h` declares the Btrfs subpage folio-state data model and helper API. It supports filesystems whose sector size or metadata node size is smaller than `PAGE_SIZE`, allowing per-sector state tracking within a single folio.

The implementation is in `subpage.c`; callers across extent I/O, metadata, delalloc, and writeback use this header to attach state and manipulate range-level flags.

## Bitmap Layout

The anonymous enum defines bitmap indexes used to build function names and offset into `btrfs_folio_state->bitmaps`:

- `btrfs_bitmap_nr_uptodate`
- `btrfs_bitmap_nr_dirty`
- `btrfs_bitmap_nr_writeback`
- `btrfs_bitmap_nr_ordered`
- `btrfs_bitmap_nr_checked`
- `btrfs_bitmap_nr_locked`
- `btrfs_bitmap_nr_max`

The comments note that ordered and checked are deprecated COW-fixup flags, while locked is currently needed for async delalloc/compression range handling.

All state bitmaps are packed into one flexible array, grouped by bitmap type and indexed by sector within the folio.

## Main Type: `struct btrfs_folio_state`

`struct btrfs_folio_state` is attached to `folio->private` for subpage data and metadata folios.

It contains:

- `lock`: protects bitmap access.
- A union:
  - `eb_refs`: metadata extent-buffer reference count, managed under mapping private lock.
  - `nr_locked`: data subpage locked-sector count.
- `bitmaps[]`: flexible bitmap storage for all per-sector state classes.

`enum btrfs_folio_type` distinguishes metadata and data allocation/attachment behavior.

## Subpage Detection

`btrfs_meta_is_subpage()` returns true when `fs_info->nodesize < PAGE_SIZE`. Metadata subpage handling depends on node size rather than folio size because metadata folios are not allocated larger than node size.

`btrfs_is_subpage()` returns true when `fs_info->sectorsize < folio_size(folio)`. For mapped data folios, it asserts the host inode is a Btrfs data inode.

## Lifecycle API

- `btrfs_attach_folio_state()`
- `btrfs_detach_folio_state()`
- `btrfs_alloc_folio_state()`
- `btrfs_free_folio_state()`

These allocate, attach, detach, and free the per-folio bitmap state.

Metadata extent-buffer reference helpers:

- `btrfs_folio_inc_eb_refs()`
- `btrfs_folio_dec_eb_refs()`

Lock tracking helpers:

- `btrfs_folio_end_lock()`
- `btrfs_folio_set_lock()`
- `btrfs_folio_end_lock_bitmap()`

## Generated Operation API

`DECLARE_BTRFS_SUBPAGE_OPS(name)` declares, for each state name:

- Strict subpage range operations:
  - `btrfs_subpage_set_name()`
  - `btrfs_subpage_clear_name()`
  - `btrfs_subpage_test_name()`
- Data folio wrapper operations:
  - `btrfs_folio_set_name()`
  - `btrfs_folio_clear_name()`
  - `btrfs_folio_test_name()`
- Clamped data folio wrapper operations:
  - `btrfs_folio_clamp_set_name()`
  - `btrfs_folio_clamp_clear_name()`
  - `btrfs_folio_clamp_test_name()`
- Metadata extent-buffer operations:
  - `btrfs_meta_folio_set_name()`
  - `btrfs_meta_folio_clear_name()`
  - `btrfs_meta_folio_test_name()`

The macro is instantiated for:

- `uptodate`
- `dirty`
- `writeback`
- `ordered`
- `checked`

The comments define expected usage:

- `btrfs_subpage_*()` assumes a subpage folio and a range inside one folio.
- `btrfs_folio_*()` handles both subpage and regular folios, but range must be inside one folio.
- `btrfs_folio_clamp_*()` truncates ranges to folio boundaries.
- Metadata should use `btrfs_meta_folio_*()` helpers, not clamped data helpers.

## Additional Helpers

`btrfs_folio_clamp_finish_io()` is an inline cleanup helper that clears dirty, sets writeback, and clears writeback for an error/finish path over a clamped range.

Dirty and diagnostics API:

- `btrfs_subpage_clear_and_test_dirty()`
- `btrfs_folio_assert_not_dirty()`
- `btrfs_meta_folio_clear_and_test_dirty()`
- `btrfs_get_subpage_dirty_bitmap()`
- `btrfs_subpage_dump_bitmap()`

## Concurrency Notes

The header documents that metadata `eb_refs` is tied to `private_lock` and protects whether `btrfs_folio_state` can be detached.

Data `nr_locked` tracks how many sectors in a folio are subpage-locked.

The bitmap layout is sized at allocation time based on `fsize >> fs_info->sectorsize_bits`.

## Integration Points

This header includes `btrfs_inode.h` for inode assertions and depends on `struct extent_buffer` declarations available through included Btrfs headers.

It is a shared contract for metadata pages, data folios, extent I/O, COW fixup state, ordered extent state, and writeback state.

## Risks And Edge Cases

The helper families are easy to misuse if a caller passes a range crossing multiple folios to non-clamp functions.

Metadata and data use the same state structure but different union fields. Passing the wrong `enum btrfs_folio_type` can corrupt logical interpretation.

The ordered and checked bits are marked deprecated but remain part of the ABI within this source file.

The locked bitmap exists for async delalloc/compression behavior and cannot be removed until that lifecycle is reworked.

## Testing Signals

Tests should validate:

- Allocation size for multiple sector counts per folio.
- Metadata vs data union initialization.
- Subpage detection for nodesize and sectorsize combinations.
- Generated helper behavior for all declared state classes.
- Clamp finish-IO behavior on partial folio ranges.
- Dirty bitmap export and debug dump paths.
