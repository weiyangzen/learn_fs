# File Research: sources/os/linux/linux/fs/nilfs2/super.c

`super.c` implements NILFS module setup, slab caches, filesystem registration, superblock commit/cleanup, mount/remount/freeze/sync/statfs behavior, snapshot mounting, checkpoint attachment, and resize.

Error handling is centralized through `__nilfs_error()`, which logs metadata inconsistency, sets `NILFS_ERROR_FS` on disk, optionally remounts read-only for `errors=remount-ro`, and can panic for `errors=panic`. Ordinary messages go through `__nilfs_msg()`.

Superblock commit code alternates/falls back between primary and secondary NILFS superblocks. `nilfs_prepare_super()` repairs one in-memory superblock copy from the other if needed and optionally flips active copies. `nilfs_commit_super()` updates write time, CRC, dirty state, flushed-device state, and calls `nilfs_sync_super()`, which uses barriers/FUA when enabled and updates GC protection sequence.

Resize updates sufile segment count, constructs a segment, moves the secondary superblock to its new end-of-device-derived location, commits both superblocks, and only then widens the allocatable segment range so log writes do not overwrite the migrating secondary superblock.

Mount setup uses the fs_context API. Supported options include `errors=`, `barrier`/`nobarrier`, read-only snapshot checkpoint `cp=`, `order=relaxed|strict`, `norecovery`, and `discard`/`nodiscard`. Snapshot mounts require read-only mode and verify the checkpoint is marked as a snapshot.

`nilfs_fill_super()` allocates and initializes `the_nilfs`, loads on-disk metadata, attaches the latest checkpoint, starts the log writer for read-write mounts, obtains the root dentry, and marks the filesystem not-clean on writable mount. Failure paths detach the writer, drop metadata inodes, delete sysfs groups, and destroy NILFS state.

The file also defines VFS `super_operations`, `file_system_type nilfs_fs_type`, cache constructors for NILFS inodes and segment buffers, module init/exit, sysfs init/exit, and registration under filesystem name `nilfs2`.
