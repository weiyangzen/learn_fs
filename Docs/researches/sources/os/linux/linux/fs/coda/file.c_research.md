# File Research: sources/os/linux/linux/fs/coda/file.c

Coda regular file operations. This file proxies file I/O to a Venus-provided host/container file while preserving Coda access-intent notifications, mmap mapping redirection, open/release, and fsync behavior.

Main data:
- `struct coda_vm_ops`: wrapper around host VMA ops with refcount, owning Coda file, host ops pointer, and copied vm ops.

Read/write/splice:
- `coda_file_read_iter()` sends Venus read access-intent begin, performs `vfs_iter_read()` on container file, then sends finish intent.
- `coda_file_write_iter()` sends write intent, writes to container file under Coda inode lock, mirrors host size/blocks to Coda inode, updates ctime/mtime, then sends finish intent.
- `coda_file_splice_read()` wraps `vfs_splice_read()` with read access-intent begin/finish.

mmap:
- `coda_file_mmap()` checks host file mmap capability, sends mmap access intent, allocates `coda_vm_ops`, switches Coda file/inode mapping to host mapping, increments inode/file map counts, calls `vfs_mmap()` on host file, then wraps VMA open/close callbacks.
- `coda_vm_open()` increments wrapper refcount and delegates to host open.
- `coda_vm_close()` delegates to host close, restores vm ops on final close, drops Coda file ref, and frees wrapper.
- Prevents new mmap if inode mapping already points at a different host mapping.

Open/release:
- `coda_open()` allocates `coda_file_info`, converts flags, calls `venus_open()` to get container file, propagates append/sync flags, initializes private data and access-intent support.
- `coda_release()` calls `venus_close()`, adjusts mmap counts/mapping, drops host file, frees private data, and returns 0 because VFS ignores release errors.

fsync:
- `coda_fsync()` waits writeback on Coda mapping, locks inode, calls `vfs_fsync()` on host file, then `venus_fsync()` when not datasync.

Registered ops:
- `coda_file_operations`: llseek, read_iter, write_iter, mmap, open, release, fsync, splice_read.
