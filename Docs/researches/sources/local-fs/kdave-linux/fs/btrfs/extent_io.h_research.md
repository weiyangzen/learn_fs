# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_io.h

This header defines the public extent I/O and extent-buffer interface used by Btrfs page-cache, metadata, btree, delalloc, readahead, and release paths.

Primary declarations:
- Extent-buffer runtime flags cover uptodate, dirty, tree reference, stale, writeback, unmapped/dummy buffers, write errors, zoned zeroout, and in-progress reads.
- Page operation bits describe batched folio actions such as unlock, start/end writeback, and ordered marking.
- `struct extent_buffer` is the in-memory representation of a metadata block, with logical start, length, folio size/shift, optional direct address, fs owner, reference state, lock, read mirror, writeback inhibitors, log-tree index, RCU head, and backing folios.
- `struct extent_changeset` records changed byte counts and optionally changed ranges, with a bytes-only sentinel to avoid allocations when callers only need accounting.
- `struct btrfs_eb_write_context` carries metadata writeback state, including zoned block group context.

Important helpers:
- `get_eb_offset_in_folio()` and `get_eb_folio_index()` hide the differences between page-sized metadata, multi-page nodes, high-order folios, and subpage metadata blocks.
- `num_extent_pages()` reports logical page slots for an extent buffer; `num_extent_folios()` reports actual populated folios.
- `extent_buffer_uptodate()` is the fast flag check for metadata block validity.

API surface:
- Data I/O: `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, `extent_write_locked_range()`, folio extent-private attach/detach, and extent mapping release.
- Metadata I/O: `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, extent-buffer read/readahead helpers, dirty/uptodate state mutation, invalidation, and release.
- Extent-buffer lifecycle: allocate, clone, dummy allocate, find, free, stale free, test-only allocation, and leak debug.
- Extent-buffer memory access: read/write/copy/memzero/memcmp/user nofault copy, bitmap set/clear/test, and full-buffer copy.
- Transaction interaction: inhibit and uninhibit extent-buffer writeback.

The header is the shared contract between inode data I/O, btree metadata I/O, transaction code, subpage support, zoned mode, fsverity-aware reads, and extent-buffer consumers.
