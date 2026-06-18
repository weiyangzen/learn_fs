# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_io.h

## Purpose

`extent_io.h` declares the public interface and core data structures for Btrfs extent I/O and metadata extent buffers. It is the contract used by Btrfs data I/O, btree I/O, folio release, metadata accessors, and delalloc helpers.

## Key Definitions

- `EXTENT_BUFFER_*` bit indexes:
  - Track extent-buffer uptodate, dirty, tree-ref, stale, writeback, unmapped, write error, zoned zeroout, and reading states.

- Page operation flags:
  - `PAGE_UNLOCK`, `PAGE_START_WRITEBACK`, `PAGE_END_WRITEBACK`, and `PAGE_SET_ORDERED` describe batched folio operations used by delalloc cleanup and writeback transitions.

- `EXTENT_FOLIO_PRIVATE`:
  - Sentinel for non-subpage data folios controlled by Btrfs extent I/O.

- Bitmap macros:
  - `BIT_BYTE`, `BITMAP_FIRST_BYTE_MASK`, and `BITMAP_LAST_BYTE_MASK` support byte-granular extent-buffer bitmap operations.

- `struct extent_buffer`:
  - Represents a Btrfs metadata block in memory.
  - Stores logical `start`, `len`, folio size/shift, state flags, fs pointer, optional contiguous `addr`, reference state, read mirror, writeback inhibitor count, log-tree index, RCU head, tree lock, and an inline folio pointer array.
  - `addr` is an optimization for physically contiguous storage that avoids cross-folio handling.

- `struct btrfs_eb_write_context`:
  - Tracks a metadata writeback control, target extent buffer, and optional zoned block group.

- `struct extent_changeset`:
  - Tracks changed byte counts and optionally changed ranges through a `ulist`.
  - Supports a bytes-only mode via `EXTENT_CHANGESET_BYTES_ONLY` to avoid atomic allocations when callers do not need range iteration.

## Inline Helpers

- `offset_in_eb_folio()` computes offsets for the extent buffer's folio size.
- `get_eb_offset_in_folio()` handles both page-sized metadata blocks and subpage nodesize cases where multiple extent buffers share one folio.
- `get_eb_folio_index()` maps an extent-buffer-relative offset to a folio slot.
- `num_extent_pages()` and `num_extent_folios()` distinguish logical page count from runtime folio count, allowing future higher-order folio support.
- `extent_buffer_uptodate()` checks the buffer-level uptodate flag.
- `wait_on_extent_buffer_writeback()` waits on the extent-buffer writeback bit.

## Exported Interface Categories

- Data I/O:
  - `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, `extent_write_locked_range()`.

- Metadata I/O:
  - `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, `read_extent_buffer_pages*()`.

- Extent-buffer lifecycle:
  - `alloc_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`.

- Extent-buffer memory access:
  - Read/write/copy/move/zero/compare helpers plus bitmap get/set/clear helpers.

- Folio and delalloc state:
  - `set_folio_extent_mapped()`, `clear_folio_extent_mapped()`, `try_release_extent_mapping()`, `try_release_extent_buffer()`, `extent_clear_unlock_delalloc()`, `extent_invalidate_folio()`.

- Allocation helpers:
  - `btrfs_alloc_page_array()` and `btrfs_alloc_folio_array()`.

- Debug/test hooks:
  - Leak checking and `find_lock_delalloc_range()` under sanity tests.

## Design Notes

The header encodes the split between data folio state and metadata extent-buffer state while hiding subpage and multi-folio details from most callers. Its helpers are carefully documented because extent-buffer offsets differ between normal nodesize >= PAGE_SIZE layouts and subpage metadata layouts.
