# File Research: sources/local-fs/kdave-linux/fs/btrfs/ioctl.c

## Purpose

`ioctl.c` is the main Btrfs user-space control-plane dispatcher. It implements `btrfs_ioctl()`, compat handling, and the backing logic for filesystem attributes, subvolume and snapshot lifecycle, device management, tree/search inspection APIs, sync/scrub/balance/quota operations, feature bits, labels, encoded I/O, io_uring encoded I/O, subvolume deletion waits, and forced shutdown.

## Public Interfaces

Exports or header-declared functions include:

- `btrfs_ioctl()`: primary ioctl switch for Btrfs files.
- `btrfs_compat_ioctl()`: compat wrapper for 32-bit callers.
- `btrfs_fileattr_get()` / `btrfs_fileattr_set()`: VFS fileattr integration.
- `btrfs_sync_inode_flags_to_i_flags()`: maps Btrfs inode flags to VFS inode flags.
- `btrfs_ioctl_get_supported_features()`: exposes supported/safe feature masks.
- `btrfs_update_ioctl_balance_args()`: snapshots live balance status into UAPI args.
- `btrfs_uring_cmd()` / `btrfs_uring_read_extent_endio()`: io_uring encoded I/O entry and completion.

## Major Behavior

File attribute handling translates between `FS_*_FL` flags and Btrfs inode flags, rejects unsupported or incompatible combinations, disallows NOCOW on zoned filesystems, manages compression properties, updates inode ctime/iversion, and persists inode changes in a transaction.

Subvolume creation and snapshot creation are transaction-heavy paths. `create_subvol()` allocates a new root objectid, anon block device, root tree block, root item, UUID tree entry, qgroup inheritance, and subvolume inode/dentry. `create_snapshot()` builds a pending snapshot and commits the transaction to materialize it. Snapshot creation coordinates with `snapshot_lock`, `snapshot_force_cow`, delalloc writeback, and ordered extent waits to prevent NOCOW races.

Subvolume deletion supports old name-based and v2 name/id-based deletion. It handles mount write counts, idmapped mount restrictions, parent dentry lookup for deletion by id, user deletion policy via `USER_SUBVOL_RM_ALLOWED`, VFS permission checks, and calls `btrfs_delete_subvolume()` under inode locking.

Tree/search ioctls implement privileged key-range iteration with bounded user buffer copying. The v1 API preserves historical overflow behavior by returning an empty item; v2 reports required size up to a 16 MiB limit. Path lookup APIs include privileged inode lookup and unprivileged lookup with read/execute permission checks while walking parent refs.

Device operations cover resize, add, remove v1/v2, device info, filesystem info, stats, and device replace. Most mutating device paths require `CAP_SYS_ADMIN`, mount write access, and Btrfs exclusive-operation coordination. Extent-tree-v2 support is explicitly rejected for several device/scrub/snapshot operations.

Space, sync, scrub, balance, and quota ioctls bridge UAPI structs to internal subsystem entry points. Balance paths distinguish new, running, paused, resumed, canceled, and progress states under `balance_mutex` plus exclusive-operation state. Quota paths serialize against `subvol_sem`, `cleaner_mutex`, and `qgroup_ioctl_lock` as needed.

Received-subvolume metadata updates modify `received_uuid`, send/receive transids and timestamps, update root items, and maintain UUID tree entries. The code prechecks UUID-tree item overflow to avoid transaction aborts from malicious input.

Feature and label ioctls read or mutate superblock fields under `super_lock`, after capability and safe-set/safe-clear validation. Feature mutations are committed through a transaction.

Encoded I/O ioctls import user iovecs, validate encoded arguments, call `btrfs_encoded_read()` or `btrfs_do_write_iter()`, and update task I/O accounting. The io_uring encoded read path can return `-EIOCBQUEUED`, retain inode/extent locks across userspace return, and complete later through task work while using lockdep annotations from `locking.h`.

`btrfs_ioctl_subvol_sync()` provides waiting and peeking over `dead_roots`, with modes for count, first/last queued deletion, one specific subvolume, and queued deletion waits. `btrfs_ioctl_shutdown()` validates flags, optionally freezes/thaws the superblock, and calls `btrfs_force_shutdown()`.

## Dependencies and Integration

This file is tightly integrated with Btrfs root/tree management, transactions, qgroups, UUID tree, volume/device code, scrub, balance, send, backrefs, defrag, fsverity, encoded I/O, and VFS permission/write-count APIs. It also depends on locking helpers from `locking.c/.h`, ordered extent waiting from `ordered-data.c`, and diagnostics from `messages.h`.

## Concurrency and Safety Notes

The file is security-sensitive: it copies many UAPI structs, validates reserved fields and flags, checks capabilities, and carefully pairs `mnt_want_write_file()` / `mnt_drop_write_file()`. Important locks include `subvol_sem`, `balance_mutex`, `ordered_extent`/snapshot DREW locks, `super_lock`, `trans_lock`, `fs_roots_radix_lock`, and VFS inode locks. Main risk areas are UAPI compatibility, lock ordering, exclusive-operation lifetime, transaction abort vs graceful error returns, and async io_uring cleanup paths.
