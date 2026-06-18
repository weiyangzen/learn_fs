# File Research: sources/os/linux/linux/fs/ubifs/super.c

Read completely: 2515 lines.

This file implements UBIFS module initialization, filesystem context parsing, VFS superblock/inode operations, mount/remount/unmount orchestration, and most per-mount resource allocation and teardown.

Main entry points: `ubifs_iget`, `ubifs_super_operations`, `ubifs_init_fs_context`, `ubifs_get_tree` through `ubifs_context_ops`, module init `ubifs_init`, and module exit `ubifs_exit`.

Inode handling: `ubifs_iget` reads an inode node from the TNC, initializes VFS inode fields, validates UBIFS inode metadata, assigns operations by file type, loads xattr/symlink/device inline data, sets UBIFS inode flags, and unlocks the inode. `ubifs_write_inode`, `ubifs_evict_inode`, `ubifs_dirty_inode`, `ubifs_drop_inode`, and slab allocation/free functions implement VFS inode lifecycle and UBIFS dirty-budget release.

Superblock operations: `ubifs_statfs` reports free space after reserved-pool adjustment; `ubifs_show_options` prints active mount options; `ubifs_sync_fs` synchronizes all journal write buffers, runs a commit, and calls `ubi_sync`.

Constants and geometry: `init_constants_early` derives UBI geometry, node length ranges, write sizes, watermarks, bulk-read buffer limits, and basic device validity before reading the superblock. `init_constants_sb` derives fanout-dependent index sizes, journal limits, budgeting constants, background-commit thresholds, and LPT geometry. `init_constants_master` computes minimum index LEBs, reported reserved-pool size, and `statfs` block count after master-node load.

Mount options: the fs-context parser handles legacy unmount mode, bulk read, data CRC checking, compressor override, assertion action, authentication key name, and authentication hash name. `ubi` and `vol` parameters are accepted as ignored compatibility strings.

Mount flow: `mount_ubifs` initializes debugging and sysfs, checks whether the UBI volume is empty, allocates buffers, initializes optional authentication, reads the superblock and master node, initializes LPT/lprops, performs free-space fixup and recovery as needed, writes dirty master/superblock updates, replays the journal, mounts orphans, reserves/cleans the GC LEB, adds the instance to the global shrinker list, initializes debugfs, and logs geometry.

Unmount and remount: `ubifs_put_super` cleanly stops the background thread, syncs write buffers, writes a clean master node unless a fatal read-only error occurred, and calls `ubifs_umount`. `ubifs_remount_rw` allocates write-only resources and completes deferred recovery, while `ubifs_remount_ro` syncs buffers, writes a clean master node, frees write-only resources, and releases LPT write state.

UBI source parsing: `open_ubi` accepts device paths plus `ubiX_Y`, `ubiY`, `ubiX:NAME`, `ubi:NAME`, and `!` separator variants. `ubifs_get_tree` opens a volume read-only for probing, uses `sget_fc` to share existing mounts, and lets `ubifs_fill_super` reopen it read-write for actual mounting.

Module lifecycle: `ubifs_init` checks node-size invariants, creates the inode slab, allocates/registers the shrinker, initializes compressors, debugfs, sysfs, and registers the filesystem. `ubifs_exit` checks that no mounts or clean znodes remain, tears down debugfs/sysfs/compressors/shrinker, waits for RCU inode frees, destroys the slab, and unregisters the filesystem.

Important interactions: this file ties together nearly every UBIFS subsystem: superblock handling, auth, LPT/lprops, master nodes, journal replay/commit, GC, orphan handling, TNC, compressors, debugfs, sysfs, shrinker, and fscrypt.

Reliability notes: mount has a long staged cleanup path matching allocation order. Read-only media, static UBI volumes, corrupted UBI volumes, format incompatibility, missing authentication support, compressor absence, and insufficient free space are all detected before exposing a usable root dentry.
