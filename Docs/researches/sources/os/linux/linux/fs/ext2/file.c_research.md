# File Research: sources/os/linux/linux/fs/ext2/file.c

Read status: complete, 343 lines.

This file implements ext2 regular-file operations, including buffered I/O dispatch, direct I/O, optional DAX I/O/fault handling, fsync, open/release, mmap preparation, and regular-file inode operations.

Key responsibilities:
- Provides DAX read/write paths with `dax_iomap_rw()` when `CONFIG_FS_DAX` and inode DAX are active.
- Provides DAX page fault handling through `dax_iomap_fault()`.
- Provides direct I/O read/write paths using `iomap_dio_rw()` and `ext2_iomap_ops`.
- Falls back from direct writes to buffered writes for unsupported cases such as holes.
- Updates file size for extending DAX/direct writes at the correct synchronization point.
- Drops reservation windows on last writable file release.
- Implements `ext2_fsync()` with metadata buffer tracking.
- Exposes `ext2_file_operations` and `ext2_file_inode_operations`.

I/O behavior:
- `ext2_file_read_iter()` dispatches to DAX, direct I/O, or generic buffered read.
- `ext2_file_write_iter()` dispatches to DAX, direct I/O, or generic buffered write.
- Direct writes force synchronous completion for unaligned or extending writes.
- Partial direct writes can continue with buffered write, then flush and invalidate the affected page-cache range.
- `ext2_dio_write_end_io()` updates `i_size` before page cache invalidation to avoid stale zeroing races.

DAX behavior:
- DAX mmap sets custom vm operations and records file access.
- DAX write faults bracket page faults with filesystem pagefault freeze protection and invalidate lock.
- Huge DAX faults are explicitly unsupported because ext2 block allocation cannot guarantee huge-page alignment.

Concurrency and safety:
- Reads take shared inode lock for DAX/direct I/O.
- Writes take exclusive inode lock.
- Release path takes `truncate_mutex` before discarding reservation state.
- Fsync reports metadata writeback I/O errors through `ext2_error()`.

Research notes:
- This file is mostly VFS/iomap plumbing; physical block mapping is delegated to `inode.c`.
- It is where ext2 integrates old indirect-block storage with modern direct I/O and DAX APIs.
