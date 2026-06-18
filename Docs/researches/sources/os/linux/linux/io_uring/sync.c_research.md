# File Research: sources/os/linux/linux/io_uring/sync.c

io_uring sync-style file operation implementation: sync_file_range, fsync, and fallocate.

Key responsibilities:
- Prepares and executes `sync_file_range()`.
- Prepares and executes `vfs_fsync_range()`, including `IORING_FSYNC_DATASYNC`.
- Prepares and executes `vfs_fallocate()`, with fsnotify modify on success.
- Forces async execution for blocking sync/allocation operations.

Important invariants:
- Unused SQE fields are rejected per opcode.
- `io_fsync_prep()` rejects negative offsets and unsupported fsync flags.
- Fsync length ending at or below zero maps to `LLONG_MAX`.
