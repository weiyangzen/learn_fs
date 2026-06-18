# File Research: sources/os/linux/linux-stable/fs/orangefs/file.c

## Scope

This file implements OrangeFS regular file operations, direct I/O transport through shared buffers, page-cache revalidation, mmap fault handling, fsync, llseek, local locks, and close flushing.

## APIs Covered

- Daemon I/O bridge: `wait_for_direct_io()`.
- Cache management: `flush_racache()`, `orangefs_revalidate_mapping()`.
- VFS file ops: read iter, splice read, write iter, mmap prepare, release, fsync, llseek, lock, flush, and `orangefs_file_operations`.

## Control Flow And Behavior

- `wait_for_direct_io()` allocates a FILE_IO op, obtains a shared-memory buffer slot, copies write data into the slot, posts the op, handles daemon restart retry with new slot/data recopy, and copies read data back to the iterator.
- OrangeFS lacks server-side open state, so kernel open mode is translated by setting upcall uid to root for permitted read/write operations to preserve POSIX open-time permission semantics.
- Read and splice paths take `i_rwsem` for read, revalidate mapping timeout, then use generic file/page-cache helpers.
- Writes beyond current size revalidate mapping before `generic_file_write_iter()`.
- mmap faults refresh file size before delegating to `filemap_fault()`.
- mmap prepare revalidates mapping, marks VMA sequential, clears random hint, sets vm ops, and records file access.
- `fsync` first writes back page cache, then sends an OrangeFS FSYNC op.
- `llseek(SEEK_END)` refreshes size before generic seek.
- Optional local locking uses VFS POSIX lock helpers only when mounted with `ORANGEFS_OPT_LOCAL_LOCK`.

## Risks And Invariants

- Shared buffer slots must be returned on every path.
- On interrupt, write semantics avoid returning `-EINTR` after data may have been written; partial write behavior depends on operation state.
- Mapping revalidation uses a bitlock to serialize invalidation, writeback, and page-cache invalidation.
- Close flush writes back local page cache but intentionally does not send server fsync.
