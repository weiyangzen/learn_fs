# File Research: sources/os/linux/linux/fs/btrfs/extent_io.h

Read completely: 412 lines.

This header declares the Btrfs extent I/O and extent-buffer interface implemented by `extent_io.c`. It defines extent-buffer flags, folio operation bits, extent-buffer layout, extent changesets, offset helpers, public data/metadata I/O entry points, and extent-buffer memory primitives.

Core definitions:
- `EXTENT_BUFFER_*` flags track uptodate, dirty, tree reference, stale, writeback, unmapped, write error, zoned zeroout, and read-in-progress state.
- `PAGE_UNLOCK`, `PAGE_START_WRITEBACK`, `PAGE_END_WRITEBACK`, and `PAGE_SET_ORDERED` describe batched folio state operations.
- `EXTENT_FOLIO_PRIVATE` marks non-subpage data folios controlled by Btrfs extent I/O.
- Bitmap macros provide byte-oriented bitmap addressing for on-disk Btrfs bitmap items.
- `struct extent_buffer` stores logical start, length, folio sizing, flags, fs pointer, optional direct address, refcount/lock state, read mirror, writeback inhibitors, log-tree index, RCU hook, rwsem tree lock, and backing folio array.
- `struct btrfs_eb_write_context` carries metadata writeback context, including zoned block group state.

Extent-buffer helpers:
- `offset_in_eb_folio()`, `get_eb_offset_in_folio()`, and `get_eb_folio_index()` hide the differences between normal page-sized metadata, larger metadata blocks, large folios, and subpage metadata.
- `num_extent_pages()` reports how many base pages a metadata block spans.
- `num_extent_folios()` reports the runtime folio count, allowing for a future large-folio-backed extent buffer.
- `extent_buffer_uptodate()` wraps the runtime uptodate flag.

Changeset support:
- `struct extent_changeset` records total changed bytes and optionally records changed ranges in a `ulist`.
- `extent_changeset_init_bytes_only()` uses a sentinel prealloc pointer to avoid range tracking when only byte counts are needed.
- Inline helpers allocate, preallocate, release, and free changesets.

Declared operations:
- Data folio I/O: `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, and `extent_write_locked_range()`.
- Btree I/O: `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, `read_extent_buffer_pages()`, and `read_extent_buffer_pages_nowait()`.
- Folio private-state helpers: `set_folio_extent_mapped()` and `clear_folio_extent_mapped()`.
- Extent-buffer lifetime: allocate, find, clone, free, stale-free, dummy allocation, test allocation, cache init/exit, and tree-block readahead.
- Extent-buffer memory access: read, write, copy, move, zero, compare, bitmap test/set/clear, dirty/uptodate state changes, and metadata dirty clearing.
- Release/invalidation helpers for folios and extent mappings.
- Writeback inhibition helpers used by transactions.

Important interactions:
- Exposes types used across Btrfs inode, btree, transaction, file, subpage, and writeback code.
- Includes Linux folio/page-cache, fiemap, btrfs tree, locks, refcount, list, and slab dependencies.
- The header is intentionally low-level: many callers use these helpers while holding Btrfs-specific locks.

Risk and correctness notes:
- The offset helpers are central for subpage metadata correctness; using plain page offsets in callers would be wrong.
- The `extent_buffer` struct is memory-sensitive and concurrency-sensitive.
- `extent_changeset` has a sentinel mode; callers must respect `extent_changeset_tracks_ranges()` before using range iteration/preallocation.
