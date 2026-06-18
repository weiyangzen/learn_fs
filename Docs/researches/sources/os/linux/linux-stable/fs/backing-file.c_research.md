# File Research: sources/os/linux/linux-stable/fs/backing-file.c

## Purpose
Provides common helpers for stackable filesystems that operate on backing files while preserving the user-visible file/path relationship.

## Main Interfaces
- `backing_file_open()`.
- `backing_tmpfile_open()`.
- `backing_file_read_iter()`, `backing_file_write_iter()`.
- `backing_file_splice_read()`, `backing_file_splice_write()`.
- `backing_file_mmap()`.

## Important Behavior
Open helpers allocate an empty backing file with supplied credentials, store the user path from the upper file, and open a real lower path or tmpfile. Read/write helpers require `FMODE_BACKING`, run under `ctx->cred`, enforce direct-I/O capability, and call optional access/end-write callbacks on the upper/original file.

Asynchronous read/write uses `struct backing_aio`, cloning the caller kiocb onto the backing file and preserving the original kiocb for completion. Async write completion is queued to the superblock DIO completion workqueue to serialize mtime/size updates, then calls the original completion callback.

Splice and mmap paths similarly switch credentials and call VFS helpers. `backing_file_mmap()` swaps `vma->vm_file` to the backing file and calls `security_mmap_backing_file()` before `vfs_mmap()`.

## Cross-File Relationships
Used by stackable filesystems such as overlayfs. Integrates with VFS open/tmpfile/read/write/splice/mmap helpers, LSM mmap checks, file privilege removal, write accounting, and superblock DIO workqueues.

## Risks / Review Notes
Async backing I/O has tight lifetime coupling among original kiocb, cloned kiocb, file refs, and completion callbacks. Write paths remove privileges from the user-facing file before writing the backing file. Mmap changes `vma->vm_file`, so security checks must see both backing and user files.
