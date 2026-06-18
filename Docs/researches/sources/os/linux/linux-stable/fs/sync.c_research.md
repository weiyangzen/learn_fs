# File Research: sources/os/linux/linux-stable/fs/sync.c

Purpose: Provides high-level sync, fsync, fdatasync, syncfs, emergency sync, and sync_file_range implementations.

Key responsibilities:
- `sync_filesystem()` writes back inode data, calls filesystem `sync_fs()` in nowait and wait phases, and syncs the backing block device.
- `ksys_sync()` implements global sync by waking flusher threads, iterating superblocks, syncing filesystem metadata, and syncing block devices.
- Implements syscalls: `sync`, `syncfs`, `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and `sync_file_range2`.
- `vfs_fsync_range()` and `vfs_fsync()` dispatch to file `f_op->fsync`, including lazytime sync for full fsync.
- `emergency_sync()` schedules async work that runs multiple sync passes.

Important interactions:
- Uses `iterate_supers()`, `sync_inodes_sb()`, `writeback_inodes_sb()`, `sync_bdevs()`, and block-device sync helpers.
- `syncfs()` reports both sync failure and accumulated writeback errors through `errseq_check_and_advance()`.

Notable invariants and risks:
- `sync_filesystem()` requires `s_umount` protection and skips read-only superblocks.
- `sync_file_range()` deliberately does not sync metadata or flush disk caches; it validates range arithmetic and allowed file types before page-cache operations.
