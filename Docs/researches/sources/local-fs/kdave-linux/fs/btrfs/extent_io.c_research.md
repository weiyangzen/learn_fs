# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_io.c

This file implements Btrfs data page-cache I/O and metadata extent-buffer I/O. It bridges folios, extent state bits, extent maps, ordered extents, bios, fsverity verification, metadata buffer cache lifetime, and btree block memory access helpers.

Major responsibilities:
- Builds and submits data read/write bios through `struct btrfs_bio_ctrl`, handling compression, readahead, checksum lookup generation hints, ordered-extent boundaries, and cgroup writeback ownership.
- Drives read folio and readahead paths with `btrfs_do_readpage()`, including extent-map lookup, holes, inline extents, compressed extent splitting, i_size zeroing, subpage locking, and fsverity verification.
- Drives buffered writeback through delalloc discovery, folio/subpage dirty bitmaps, ordered extent creation, COW fixup, sector submission, and ordered extent completion/error cleanup.
- Implements btree metadata writeback through the extent-buffer xarray marks, dirty/writeback flags, zoned metadata write-pointer coordination, and metadata bio end I/O.
- Allocates, finds, clones, reads, releases, and frees `struct extent_buffer` objects, including subpage metadata folio state and RCU-delayed frees.
- Provides byte, bitmap, memcpy/memmove, memset, and user-copy helpers over extent buffers that may span multiple folios or have a direct contiguous address.

Key data flows:
- `btrfs_read_folio()` and `btrfs_readahead()` lock the inode IO-tree range, wait or skip ordered extents as appropriate, map file offsets through extent maps, submit data bios, then unlock extent state.
- `btrfs_writepages()` serializes zoned data relocation, walks dirty folios in `extent_write_cache_pages()`, runs delalloc with `writepage_delalloc()`, submits sectors with `extent_writepage_io()`, and flushes the pending write bio at the end.
- `btree_writepages()` walks the filesystem `buffer_tree` xarray by dirty/towrite marks, locks dirty extent buffers, verifies zoned metadata placement, then writes each extent buffer with `write_one_eb()`.
- `alloc_extent_buffer()` obtains or creates the xarray-cached metadata buffer for a logical tree block, attaches folios to the btree inode page cache, handles races with existing buffers, and installs the tree reference.
- Metadata reads use `read_extent_buffer_pages_nowait()` to submit a metadata bio and validate parent checks in `end_bbio_meta_read()` before setting extent-buffer uptodate state.

Concurrency and lifetime:
- Data folio state is coordinated through folio locks, Btrfs subpage state, the inode IO tree, ordered extent locks, and writeback control.
- Extent buffers use `fs_info->buffer_tree` xarray membership, `refs_lock`, `EXTENT_BUFFER_TREE_REF`, `EXTENT_BUFFER_STALE`, dirty/writeback bits, and RCU freeing to avoid races with lookup, release_folio, and I/O completion.
- Btree writeback marks are stored in the buffer-tree xarray rather than the normal page-cache tags alone.
- Transaction writeback inhibition is tracked in `trans->writeback_inhibited_ebs` and suppresses opportunistic writeback while keeping references to inhibited buffers.

Important invariants:
- Delalloc ranges must be locked in folio order, rechecked under the IO-tree lock, and cleaned up if ordered extent setup partially fails.
- Data write bios must not cross ordered extent boundaries, especially for zoned filesystems.
- Compressed reads must not merge separate extent maps that point to the same compressed on-disk extent with different logical offsets.
- Extent buffers must be aligned to sectorsize/nodesize constraints and must not be freed while dirty, under writeback, or reachable through the tree reference.
- Extent-buffer memory helpers check ranges and preserve correct subpage offsets for nodesize smaller than page size.
