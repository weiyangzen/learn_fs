# File Research: sources/os/linux/linux/fs/sync.c

Purpose: High-level implementation of `sync`, `syncfs`, `fsync`, `fdatasync`, and `sync_file_range` behavior.

Key APIs and syscalls:
- `sync_filesystem(sb)` writes back inodes, invokes `s_op->sync_fs()` in nowait and wait phases, syncs block device cache, and requires `s_umount` to be held.
- `ksys_sync()` and `SYSCALL_DEFINE0(sync)` sync all superblocks and block devices.
- `emergency_sync()` schedules asynchronous emergency writeback work.
- `SYSCALL_DEFINE1(syncfs)` syncs one filesystem and reports writeback errors via `errseq_check_and_advance`.
- `vfs_fsync_range()` and `vfs_fsync()` are exported helpers for file operation `->fsync`.
- `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and `sync_file_range2` syscalls are implemented.

Implementation notes:
- Global sync wakes flusher threads first, then iterates superblocks to sync inodes and filesystem metadata, then syncs block devices.
- `sync_file_range()` validates flags and signed offsets, handles 32-bit pagecache address limits, supports wait-before/write/wait-after ordering, and only accepts regular files, block devices, and directories.
- `sync_file_range()` explicitly does not sync metadata or flush disk caches; comments document application-visible limitations.

Concurrency and correctness:
- `syncfs` holds `sb->s_umount` around `sync_filesystem`.
- Emergency sync runs from workqueue context and performs two passes to reduce missed locked pages.
- `sync_file_range` propagates writeback errors from wait operations.
