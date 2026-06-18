# File Research: sources/os/linux/linux/fs/backing-file.c

## Summary
Provides common helpers for stackable filesystems that operate on backing files while preserving the user-visible file/path context.

## Main Responsibilities
- Open backing files and tmpfiles with supplied credentials.
- Attach the user-facing path to backing file containers.
- Provide read/write/splice/mmap helpers under backing credentials.
- Support async backing I/O completion and position propagation.
- Remove privileges before backing writes.
- Call filesystem-provided access and write-end hooks.

## Key APIs
- `backing_file_open()`, `backing_tmpfile_open()`.
- `backing_file_read_iter()`, `backing_file_write_iter()`.
- `backing_file_splice_read()`, `backing_file_splice_write()`.
- `backing_file_mmap()`.

## Important Behavior
Backing files must have `FMODE_BACKING`; helpers warn and fail otherwise. Synchronous kiocbs call normal VFS iter read/write helpers. Asynchronous reads/writes clone the original kiocb into `struct backing_aio`, hold the backing file, and propagate `ki_pos` back to the original kiocb on cleanup.

Async writes queue completion to the original file superblock’s `s_dio_done_wq` so mtime/size updates are serialized. Direct I/O is rejected if the backing file cannot support it.

Reads and mmap invoke `ctx->accessed` on the user file. Writes and splice writes call `file_remove_privs()` on the user-visible file before writing to the backing file and call `ctx->end_write` when present.

`backing_file_mmap()` temporarily swaps `vma->vm_file` to the backing file, runs `security_mmap_backing_file()`, and then calls `vfs_mmap()`.

## Risks
This layer bridges user-visible and real backing file state, so credential scoping, file refs, position propagation, direct-I/O capability checks, mmap security hooks, and async completion ordering are all important. Async write completion relies on `s_dio_done_wq` initialization.
