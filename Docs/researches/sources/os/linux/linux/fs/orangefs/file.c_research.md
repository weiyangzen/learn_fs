# File Research: sources/os/linux/linux/fs/orangefs/file.c

Implements OrangeFS regular file operations and the shared-memory direct I/O RPC helper.

Key behavior:
- `wait_for_direct_io()` allocates an operation, obtains a bufmap slot, copies write data into shared buffers, submits `ORANGEFS_VFS_OP_FILE_IO`, handles daemon restart retries, copies read data back to the iterator, and releases slot/op state.
- It uses uid `0` for I/O when VFS open mode already proved read/write access, preserving POSIX open-time permission semantics despite OrangeFS server-side per-I/O permission checks.
- `orangefs_revalidate_mapping()` serializes cache invalidation with a bitlock, writes back dirty pages, invalidates page cache, and refreshes a mapping timeout.
- Read and splice-read paths revalidate mapping under `i_rwsem` before using generic filemap reads.
- Write path revalidates mapping for writes beyond current size, then uses generic buffered write.
- `orangefs_fault()` refreshes file size before mmap faults; `orangefs_file_mmap_prepare()` revalidates mapping and installs vm ops.
- `orangefs_file_release()` flushes daemon readahead cache when enabled and page cache has pages.
- `orangefs_fsync()` writes back page cache, then sends `ORANGEFS_VFS_OP_FSYNC`.
- `orangefs_file_llseek()` refreshes size for `SEEK_END`.
- `orangefs_lock()` supports local-only POSIX locks when mounted with `local_lock`.
- `orangefs_flush()` writes back local page cache on close without sending server fsync.

Important exported table:
- `orangefs_file_operations` wires llseek/read/write/lock/mmap/open/splice/flush/release/fsync/setlease.
