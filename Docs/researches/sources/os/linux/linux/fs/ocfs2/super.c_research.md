# File Research: sources/os/linux/linux/fs/ocfs2/super.c

## Purpose

`super.c` implements OCFS2 module initialization, filesystem registration, fs_context parsing, superblock probing and initialization, mount and dismount flow, quota setup, system inode initialization, statfs, memory-cache management, debugfs reporting, and OCFS2 error/abort behavior.

## Module and Filesystem Registration

Module initialization in `ocfs2_init()`:

- Initializes the OCFS2 metadata uptodate cache.
- Creates inode/dquot/quota chunk slab caches.
- Creates top-level debugfs directory `ocfs2`.
- Sets the OCFS2 locking protocol.
- Registers the OCFS2 quota format.
- Registers the `ocfs2` filesystem type.

Exit reverses these operations and unregisters the filesystem.

`ocfs2_fs_type` uses:

- `.name = "ocfs2"`
- `.kill_sb = kill_block_super`
- `.fs_flags = FS_REQUIRES_DEV | FS_RENAME_DOES_D_MOVE`
- `.init_fs_context = ocfs2_init_fs_context`
- `.parameters = ocfs2_param_spec`

## Mount Options

`struct mount_options` stores parsed options:

- Commit interval, mount option bitmask, atime quantum, preferred slot.
- Localalloc size option.
- Reservation levels for file and directory allocation.
- Cluster stack label and whether it is a userspace stack.

`ocfs2_param_spec` supports options including:

- `barrier`
- `errors=panic|remount-ro|continue`
- `intr` / `nointr`
- `heartbeat=local|none|global`
- `data=writeback|ordered`
- `atime_quantum`
- `preferred_slot`
- `commit`
- `localalloc`
- `localflocks`
- `cluster_stack`
- `user_xattr`
- `inode64`
- `acl`
- `usrquota`
- `grpquota`
- `coherency=buffered|full`
- `resv_level`
- `dir_resv_level`
- `journal_async_commit`

`ocfs2_check_set_options()` validates heartbeat mode exclusivity for non-userspace stacks, quota feature availability, ACL feature availability, and default ACL behavior based on xattr feature support.

`ocfs2_reconfigure()` handles remount:

- Syncs the filesystem first.
- Rejects heartbeat mode, data mode, and enabling `inode64` changes on remount.
- Handles readonly transitions, including quota suspend/resume/enable.
- Refuses read-write remount when hard-readonly, error-marked, or unsupported readonly-compatible features are present.

`ocfs2_show_options()` emits mount options for `/proc/mounts`.

## Superblock Probe and Verification

`ocfs2_sb_probe()`:

- Determines logical sector size and clamps minimum to OCFS2 minimum.
- Checks block zero for old OCFS1 headers/signatures and rejects them.
- Probes possible OCFS2 block sizes from sector size through 4096 bytes at `OCFS2_SUPER_BLOCK_BLKNO`.
- Calls `ocfs2_verify_volume()` for each candidate.

`ocfs2_verify_volume()`:

- Checks superblock signature.
- Validates metadata ECC if the feature is present.
- Verifies blocksize bits, actual probed block size, OCFS2 major/minor revision, superblock block number, cluster size bits, root/system directory block numbers, and max slots.
- Returns `-EAGAIN` when the candidate block size is not the superblock.

## OSB Initialization

`ocfs2_initialize_super()` allocates and fills `struct ocfs2_super`:

- Installs super operations, dentry ops, export ops, quota ops, xattr handlers, time granularity, and default `SB_NOATIME`.
- Calculates `s_maxbytes` using `ocfs2_max_file_offset()`.
- Copies UUID into VFS superblock and builds OCFS2 UUID string.
- Initializes locks, waitqueues, work items, node maps, allocation stats, reservation maps, orphan scan/recovery state, refcount tree, quota work, and local allocation state.
- Reads feature flags and rejects unsupported incompat features, or unsupported ro-compat features for read-write mounts.
- Copies cluster stack/name information if valid.
- Allocates journal state and DLM debug state.
- Loads root, system directory, and global system inodes.
- Locates the global bitmap inode and records bitmap block, cluster count at boot, and bitmap bits per group.
- Initializes slot info and the ordered workqueue.

Cleanup labels unwind allocated OSB substructures in reverse order.

## Mount Flow

`ocfs2_fill_super()`:

- Probes and initializes the superblock.
- Applies parsed options, localalloc sizes, and reservation levels.
- Verifies userspace stack compatibility with on-disk cluster info.
- Handles readonly block devices:
  - Requires readonly mount.
  - Rejects local heartbeat.
  - Checks journals without cluster locks.
  - Sets hard-readonly and skips cluster services/recovery.
- Verifies heartbeat constraints.
- Creates debugfs entries and ECC stats debugfs when enabled.
- Calls `ocfs2_mount_volume()`.
- Builds the VFS root dentry from `osb->root_inode`.
- Creates per-device `/sys/fs/ocfs2/<devname>` kset and filecheck sysfs.
- Completes mount recovery, logs mount details, enables quotas on read-write mounts, completes quota recovery, and starts orphan scanning.

`ocfs2_mount_volume()` for non-hard-readonly mounts:

- Initializes DLM.
- Takes the super lock.
- Finds/claims this node's slot.
- Loads local system inodes.
- Checks/replays journal state and local alloc state through `ocfs2_check_volume()`.
- Initializes truncate log.
- Releases the super lock.

`ocfs2_check_volume()`:

- Initializes the journal and verifies the journal can address the full volume.
- Wipes clean journals or loads dirty journals for replay.
- Configures JBD2 async commit feature according to mount option.
- Begins local allocation recovery for dirty local journals.
- Loads local allocation.
- Marks dead nodes and computes replay slots.

## Dismount Flow

`ocfs2_put_super()` syncs the block device and calls `ocfs2_dismount_volume()`.

`ocfs2_dismount_volume()`:

- Removes filecheck sysfs and per-device kset.
- Stops orphan scan and quota recovery.
- Disables quotas and drains quota drop work.
- Shuts down local allocation and truncate log.
- Exits recovery and syncs the block device.
- Purges refcount trees.
- Takes the super lock if cluster connection exists, releases this node's slot, then unlocks.
- Releases system inodes and shuts down journal.
- Determines whether cluster heartbeat hangup is needed.
- Shuts down DLM and, if needed, calls `ocfs2_cluster_hangup()`.
- Removes debugfs/ECC stats, marks dismounted, logs unmount, deletes OSB, and clears `sb->s_fs_info`.

`ocfs2_delete_osb()` destroys the workqueue, frees slot info, orphan wipe arrays, journal, local alloc copy, UUID string, volume label, and DLM debug state, then clears the OSB memory.

## System Inodes and Slab Caches

- `ocfs2_init_global_system_inodes()` loads root, system directory, and global online system inodes.
- `ocfs2_init_local_system_inodes()` loads all local-slot system inodes needed for the mounted slot.
- `ocfs2_release_system_inodes()` drops global and local cached inode references and frees the local inode array.
- `ocfs2_alloc_inode()` allocates `ocfs2_inode_info`, initializes journal inode state and dquot pointers.
- `ocfs2_inode_init_once()` initializes inode locks, extent map, IO markers, allocation semaphores, metadata cache, lock resources, and VFS inode base.

## Quotas

Quota helpers:

- `ocfs2_enable_quotas()` loads local user/group quota system inodes and enables quota usage accounting.
- `ocfs2_disable_quotas()` disables loaded quotas, cancels sync work, and lets global quota files receive synced dquot state.
- `ocfs2_susp_quotas()` suspends or resumes quotas around readonly remount transitions.

Quota support depends on `OCFS2_FEATURE_RO_COMPAT_USRQUOTA` and `OCFS2_FEATURE_RO_COMPAT_GRPQUOTA`.

## Debugfs and Statfs

With `CONFIG_DEBUG_FS`, `ocfs2_osb_dump()` produces a one-page textual state dump containing device, volume, size, feature, mount, cluster, recovery, commit, journal, allocation, local alloc, steal slot, orphan scan, and slot generation data.

`ocfs2_statfs()` locks the global bitmap inode, reads total and used bits, and fills `kstatfs`, including a two-part fsid generated from CRC32 over the UUID string.

## Error Handling

- `ocfs2_handle_error()` marks the OSB error flag and applies the selected `errors=` behavior:
  - Panic.
  - Return `-EIO`.
  - Default remount-readonly behavior with `OCFS2_OSB_SOFT_RO`.
- `__ocfs2_error()` logs the function name and formatted corruption message, then calls `ocfs2_handle_error()`.
- `__ocfs2_abort()` logs a critical abort and forces panic behavior for clustered mounts.
- `ocfs2_block_signals()` / `ocfs2_unblock_signals()` wrap in-kernel signal mask changes.

## Correctness Notes

- Hard-readonly mounts skip cluster services and recovery and require journals to be clean enough for readonly access.
- Userspace stack mounts must pass a cluster stack matching the on-disk stack label.
- Quotas are enabled after mount recovery because cluster lock recovery may be needed before quota operations can safely wait.
- `ocfs2_show_options()` appears to print `osb->osb_resv_level` for `dir_resv_level` rather than `osb->osb_dir_resv_level`; this is worth checking if mount option display accuracy matters.
