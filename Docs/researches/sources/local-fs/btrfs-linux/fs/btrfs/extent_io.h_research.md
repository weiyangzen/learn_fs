# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.h

## Scope

This header defines the public data structures, flags, inline helpers, and exported APIs for Btrfs extent-buffer metadata blocks and folio/page-cache I/O support implemented in `extent_io.c`.

## Types And Data Structures

- The extent-buffer flag enum defines UPTODATE, DIRTY, TREE_REF, STALE, WRITEBACK, UNMAPPED, WRITE_ERR, ZONED_ZEROOUT, and READING bits.
- The page operation enum defines flags used by contiguous folio processing: unlock, start writeback, end writeback, and set ordered.
- `EXTENT_FOLIO_PRIVATE` is the non-subpage folio-private sentinel for folios managed by Btrfs extent state.
- Bitmap macros define byte-granular addressing and first/last byte masks for extent-buffer bitmap items.
- `struct extent_buffer` models a metadata tree block in memory: logical bytenr, nodesize length, backing folio geometry, direct address if possible, flags, fs_info, refcounting, read mirror, writeback inhibitors, log index, RCU head, tree lock, and inline folio array.
- `struct btrfs_eb_write_context` carries writeback control plus the target EB and zoned block group.
- `struct extent_changeset` records bytes changed and optionally a `ulist` of changed ranges for extent-state operations.

## Inline Helpers

- `offset_in_eb_folio()` and `get_eb_offset_in_folio()` compute offsets for normal and subpage/nodesize-less-than-page cases.
- `get_eb_folio_index()` maps an EB-relative offset to the backing folio index.
- `extent_changeset_init()`, `extent_changeset_init_bytes_only()`, `extent_changeset_prealloc()`, `extent_changeset_release()`, and `extent_changeset_free()` manage optional changed-range tracking.
- `wait_on_extent_buffer_writeback()` waits for EB metadata writeback completion.
- `num_extent_pages()` and `num_extent_folios()` compute backing page/folio counts while allowing future high-order folios.
- `extent_buffer_uptodate()` tests EB UPTODATE state.
- UUID header writers wrap `write_extent_buffer()` for fsid/chunk tree UUID fields.

## Public API Surface

The header exposes data read/write/readahead entry points, delalloc clearing, release/invalidate helpers, data folio mapping helpers, extent-buffer allocation/lookup/free/clone, metadata reads, metadata writeback wait, metadata dirty/uptodate state changes, EB byte operations, bitmap operations, page/folio array allocation helpers, debug leak checks, sanity-test allocation, and transaction-scoped EB writeback inhibition.

## Dependencies And Consumers

It includes core kernel folio, rbtree, refcount, rwsem, list, fiemap, and Btrfs tree definitions, and forward-declares Btrfs inode/root/fs/transaction types. Consumers include btree block management, disk I/O, tree modification code, inode read/write paths, compression, fsync/logging, zoned metadata writeback, free-space and extent-tree code, and tests.

## Risks And Invariants

- `struct extent_buffer` assumes at most `INLINE_EXTENT_BUFFER_PAGES` folios, derived from maximum metadata block size and page size.
- EB offset helpers must handle both sectorsize equal to page size and subpage nodesize cases.
- Folio-private values differ between regular and subpage modes; callers must use the helpers rather than interpreting private pointers directly.
- `extent_changeset` can be bytes-only; callers must check `extent_changeset_tracks_ranges()` before using the ulist as a range list.
- Most EB access functions assume the EB has been read and validated or is explicitly unmapped/dummy.
