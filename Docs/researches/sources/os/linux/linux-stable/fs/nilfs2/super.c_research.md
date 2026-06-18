# File Research: sources/os/linux/linux-stable/fs/nilfs2/super.c

`super.c` implements NILFS module registration, slab cache setup, superblock operations, mount context parsing, mount/reconfigure flow, filesystem resize, dual-superblock commit logic, snapshot attachment, and error handling.

Logging and error handling are centralized through `__nilfs_msg()` and `__nilfs_error()`. Metadata corruption calls set `NILFS_ERROR_FS` on on-disk superblocks, may remount read-only for `errors=remount-ro`, and may panic for `errors=panic`. `nilfs_alloc_inode()` initializes NILFS-specific inode fields; `nilfs_free_inode()` destroys metadata-private state before returning the inode object to the slab.

Superblock persistence uses two superblocks. `nilfs_prepare_super()` repairs/copies from the valid twin if one magic is bad and can flip active superblocks. `nilfs_commit_super()` updates write time and CRC, optionally both copies, clears dirty state, marks the device flushed, and calls `nilfs_sync_super()`. `nilfs_sync_super()` uses barriers/FUA when enabled, falls back to the alternate superblock after I/O failure, and updates GC protection sequence. `nilfs_cleanup_super()` restores clean state on unmount/remount-ro/freeze and commits one or both copies depending on checkpoint alignment.

`nilfs_resize_fs()` validates requested size against device size and minimum constraints, takes the segment-constructor write lock while resizing sufile segment count, forces segment construction, relocates the secondary superblock, updates device size and segment count in both superblocks, commits all, and only then expands the allocatable segment range. That ordering protects the secondary superblock location during expansion.

Super operations include inode allocation/free, dirty/evict hooks, put_super, sync_fs, freeze/unfreeze, statfs, and show_options. `nilfs_sync_fs()` may construct a segment, commits dirty superblock state, and flushes the block device. `nilfs_statfs()` computes blocks from segment geometry, subtracts reserved segment blocks from available space, and queries ifile for inode counts with an `-ERANGE` fallback.

Mount options are parsed through fs_context: `errors=`, `barrier/nobarrier`, `cp=`, `order=relaxed|strict`, `norecovery`, and `discard/nodiscard`. `cp=` is invalid on remount and requires read-only mounting. Default options are `errors=remount-ro` and barrier enabled.

Mounting flows through `nilfs_get_tree()` and `nilfs_fill_super()`. `nilfs_fill_super()` allocates and initializes `the_nilfs`, installs super/export operations, loads NILFS metadata, sets UUID/sysfs name, attaches the latest checkpoint, starts the log writer for read-write mounts, builds the root dentry, and marks the superblock mounted/dirty as needed. Snapshot mounts validate that the checkpoint is a snapshot and attach a root dentry for that checkpoint. Existing superblocks are reused carefully, rejecting conflicting read-only/read-write mounts when the live tree is busy.

Reconfiguration handles read-write to read-only by syncing and cleaning the superblock, and read-only to read-write by checking unsupported read-only-compatible features, clearing `SB_RDONLY`, attaching the log writer, and setting up the superblock. It refuses remount when recovery is incomplete.

The bottom of the file registers `nilfs_fs_type`, allocates/destroys slab caches for inodes, transaction contexts, segment buffers, and btree paths, initializes sysfs, registers/unregisters the filesystem, and provides module init/exit.
