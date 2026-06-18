# File Research: sources/os/linux/linux/fs/jffs2/file.c

This file implements regular-file VFS operations and address-space operations.

`jffs2_file_operations` wires generic llseek/open/read/write/splice/lease helpers, `jffs2_ioctl()`, read-only mmap prepare, and `jffs2_fsync()`. `jffs2_fsync()` waits for writeback over the requested range, locks the inode, and triggers `jffs2_flush_wbuf_gc()` for that inode to flush pending write-buffer data.

`jffs2_file_inode_operations` provides ACL, setattr, and xattr listing hooks. `jffs2_file_address_operations` provides `read_folio`, `write_begin`, and `write_end`.

`jffs2_do_readpage_nolock()` maps a folio, reads a PAGE_SIZE range through `jffs2_read_inode_range()`, marks the folio uptodate on success, and flushes dcache. `jffs2_read_folio()` serializes with `f->sem`; `__jffs2_read_folio()` is the unlocked helper used by GC page reads.

`jffs2_write_begin()` handles sparse extension before the write by creating a zero-compressed hole node from old EOF to the new position. It then locks `c->alloc_sem`, obtains the target folio, and reads it in under `f->sem` if not uptodate. The alloc semaphore prevents a GC/page-cache deadlock while a page is being brought uptodate.

`jffs2_write_end()` writes back actual data from the folio. It allocates a raw inode, fills identity/mode/uid/gid/size/time fields, maps the folio from an aligned start offset, calls `jffs2_write_inode_range()`, adjusts the returned written length for alignment padding, updates inode size/blocks/timestamps, clears uptodate on partial write, and releases the folio.

Key dependencies: `read.c`, `write.c`, compression through `jffs2_write_inode_range()`, VFS folio APIs, CRC32, and writebuffer flush support.

Important locking: regular reads use `f->sem`; write begin additionally uses `c->alloc_sem` while acquiring/reading the page to avoid GC deadlocks.
