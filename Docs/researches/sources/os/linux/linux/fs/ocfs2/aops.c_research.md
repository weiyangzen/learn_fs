# File Research: sources/os/linux/linux/fs/ocfs2/aops.c

OCFS2 address-space operations implementation. This file connects Linux VFS/page-cache operations to OCFS2 extent mapping, inline-data handling, journaling, quota accounting, direct I/O completion, and cluster-safe inode locking.

Key exported/global interfaces:
- `const struct address_space_operations ocfs2_aops`: installs OCFS2 handlers for read, readahead, writepages, buffered writes, bmap, direct I/O, invalidation, release, migration, and partial-uptodate checks.
- `ocfs2_get_block()`: maps logical file blocks to physical blocks through the OCFS2 extent map. It treats sparse holes and unwritten extents carefully and never allocates here.
- `ocfs2_read_inline_data()` and `ocfs2_size_fits_inline_data()`: helpers for inline-data files.
- `ocfs2_map_folio_blocks()`, `ocfs2_write_begin_nolock()`, `ocfs2_write_end_nolock()`, and `ocfs2_unlock_and_free_folios()`: shared write-path helpers used by buffered, mmap, and direct write paths.
- `walk_page_buffers()`: ext3-derived helper for iterating buffer_heads in a page range.

Major behavior:
- Symlink block mapping is special-cased through `ocfs2_symlink_get_block()`, including a buffer-cache-to-page-cache copy for newly created symlinks whose data may still be journaled.
- Read path takes the inode cluster lock and `ip_alloc_sem`; `read_folio` handles inline-data files and zeroes folios beyond updated `i_size` after remote truncation.
- Readahead uses nonblocking inode locking and skips inline data, remote truncation, and allocation semaphore contention.
- Writeback delegates to `mpage_writepages()` with `ocfs2_get_block()`, relying on preexisting block mappings for dirty pages.
- `bmap` refuses refcounted inodes because swap-style bypass I/O cannot safely interact with CoW/refcount semantics.
- Buffered writes allocate and populate an `ocfs2_write_ctxt`, possibly convert inline data to extents, zero sparse tails or expand nonsparse files, CoW refcounted extents, lock allocators, start transactions, prepare folios, allocate/write clusters, update inode size/timestamps, and commit journal state.
- Direct writes use `ocfs2_dio_wr_get_block()` to allocate/map one cluster-sized range at a time, may add growing writes to the orphan directory, and defer unwritten extent conversion plus `i_size` updates to `ocfs2_dio_end_io_write()`.
- Unwritten extent coordination uses inode-local `ip_unwritten_list` plus per-write/per-DIO lists to avoid double-zeroing and defer `OCFS2_EXT_UNWRITTEN` clearing until I/O completion.
- Inline writes are attempted for empty or already-inline files when the write fits and is not mmap-based; otherwise the inode is converted to extents.

Important invariants and locking:
- Extent lookups and modifications are serialized with `OCFS2_I(inode)->ip_alloc_sem`; normal buffered writes take it for write, reads take it for read.
- Metadata changes require inode cluster locks and journal access to the dinode buffer.
- Write context folios are unlocked before cached deallocs run to avoid journal transaction barrier deadlocks.
- Direct-I/O end completion expects the submitting iocb to retain an OCFS2 rw-lock bit in `iocb->private`; completion clears the bit and unlocks.
- Newly allocated or partially failed write ranges are zeroed and marked dirty/uptodate to avoid stale data exposure.
- Sparse holes in `ocfs2_get_block()` are treated as holes if sparse allocation is enabled; holes on nonsparse files are logged as corruption-like I/O errors.

Dependencies:
- Core OCFS2 modules: allocation, extent map, inode, journal, suballoc, super, refcount tree, directory/namei/sysfile helpers.
- Linux helpers: buffer_head, folios, mpage, direct I/O, quota, block device, page cache, JBD2 handles.
