# File Research: sources/os/linux/linux-stable/fs/ocfs2/aops.c

## Summary
Implements OCFS2 address-space operations for file data: block mapping, inline-data reads/writes, folio read/readahead/writeback, buffered write preparation/completion, mmap write preparation support, direct I/O mapping/completion, unwritten extent conversion, and exported `ocfs2_aops`.

## Main Responsibilities
- Translate logical file blocks/clusters to physical blocks through the extent map.
- Support special symlink mapping and inline-data file reads/writes.
- Coordinate page-cache reads, readahead, writepages, bmap, folio release, and migration hooks.
- Prepare buffered, mmap, and direct writes with cluster allocation, quota, journaling, COW, unwritten extent, and non-sparse-extension handling.
- Zero newly allocated or partially initialized regions to prevent stale data exposure.
- Track direct-I/O unwritten extents and finalize them after I/O completion.
- Maintain inode size, timestamps, block counts, dinode fields, and fsync transaction state after writes.

## Key Interfaces
- `ocfs2_get_block()` maps normal data and symlink data for buffer-head users.
- `ocfs2_read_inline_data()` and `ocfs2_size_fits_inline_data()` are shared inline-data helpers.
- `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` are the reusable write core for buffered, mmap, and direct paths.
- `ocfs2_map_folio_blocks()` maps buffer heads within folios after extent decisions are already made.
- `ocfs2_direct_IO()` selects read/write get-block callbacks for `__blockdev_direct_IO()`.
- `ocfs2_aops` installs the address-space operation table.

## Important Behavior
`ocfs2_get_block()` never allocates. It maps existing extents, treats unwritten extents as holes for zeroing, marks buffers new only for writes past EOF, and rejects missing mappings on non-sparse files.

Buffered reads take the inode cluster lock and `ip_alloc_sem`, then choose inline-data reads or `block_read_full_folio()`. Readahead uses nonblocking inode locking and ignores difficult cases.

Writes allocate an `ocfs2_write_ctxt`, optionally keep data inline, zero sparse tails, expand non-sparse files, perform refcount COW, build per-cluster descriptors, lock allocators, start a journal transaction, grab all affected folios, allocate or mark extents written, map buffers, and later commit written ranges and inode metadata.

Direct writes use a custom `ocfs2_dio_write_ctxt`. Extending direct I/O may add the inode to the orphan directory before allocating blocks, then `ocfs2_dio_end_io_write()` converts unwritten extents, advances i_size, removes the orphan entry, and releases deferred metadata.

## State and Synchronization
The file relies on OCFS2 inode locks, rw locks held by higher file I/O paths, `ip_alloc_sem`, folio locks, buffer-head state, JBD2 handles, quota reservations, `ip_unwritten_list` under `ip_lock`, and cached deallocation contexts.

## Cross-File Interactions
It depends on extent mapping/allocation, inode locking, journaling, refcount COW, truncate-log freeing, orphan directory management, quota, and directory/sysfile helpers. `file.c`, mmap code, and other OCFS2 write paths call the nolock write helpers.

## Risks
The most sensitive areas are stale-data prevention during allocation failure, direct-I/O unwritten extent cleanup, orphan handling for extending DIO, inline-to-extent conversion, and lock ordering between page locks, journal locks, inode locks, and `ip_alloc_sem`.
