# File Research: sources/os/linux/linux-stable/fs/btrfs/ioctl.c

## Summary
Implements the Btrfs ioctl surface, including subvolume and snapshot management, device management, tree search, inode/path lookup, qgroups, scrub, balance, feature flags, filesystem labels, encoded I/O, io_uring encoded commands, shutdown, and compatibility handling.

## Main Responsibilities
- Translates VFS file attributes and legacy FS flags to/from Btrfs inode flags.
- Creates, snapshots, deletes, sync-waits, and flags subvolumes.
- Handles filesystem/device operations: resize, add/remove device, default subvolume, filesystem/device info, stats, replace, trim, label, feature bits, and shutdown.
- Exposes privileged metadata queries: tree search, inode lookup, inode-to-path, logical-to-inode, subvolume info/rootrefs, space info.
- Drives long-running exclusive operations: relocation-backed resize/remove, balance, scrub, and device replace.
- Handles qgroup enable/disable, create/remove, assign, limit, rescan, status, and wait.
- Bridges Btrfs encoded read/write APIs to ioctl and io_uring command paths.
- Provides 32-bit compat layouts for selected packed UAPI structs.

## Key APIs
- `btrfs_ioctl()`, `btrfs_compat_ioctl()`.
- `btrfs_fileattr_get()`, `btrfs_fileattr_set()`.
- `btrfs_sync_inode_flags_to_i_flags()`.
- `btrfs_ioctl_get_supported_features()`.
- `btrfs_update_ioctl_balance_args()`.
- `btrfs_uring_cmd()`, `btrfs_uring_read_extent_endio()`.

## Important Behavior
File attribute setting rejects unsupported FSX attributes, validates incompatible compression/NOCOW flag combinations, disallows NOCOW on zoned filesystems, updates compression properties, updates inode version/ctime, and persists inode metadata in a transaction.

Subvolume creation allocates a new root item, tree block, anon device, root UUID item, qgroup inheritance, and subvolume inode under metadata reservation. Snapshot creation forces prior delalloc writeback, toggles `snapshot_force_cow`, waits ordered extents, then commits a pending snapshot. Extent tree v2 currently rejects snapshotting and snapshot deletion.

Subvolume deletion supports legacy name lookup and v2 by-name/by-id deletion. By-id deletion may locate a parent outside the caller’s mount point and restricts idmapped mounts to avoid deleting unrelated subvolumes through idmap privilege differences.

Tree search copies headers/items to user buffers using nofault copies after subpage fault-in to avoid livelock. V1 preserves historical overflow behavior by returning an empty item; v2 reports required buffer size on `-EOVERFLOW`.

Device resize/add/remove, balance, and device replace use Btrfs exclusive-operation state to prevent conflicting mutating operations. Resize and device removal support `"cancel"` paths that signal relocation cancellation and wait for running relocation state.

Encoded reads validate privilege and iovec input, call `btrfs_encoded_read()`, then handle regular encoded extents synchronously if `-EIOCBQUEUED` is returned. Encoded writes require write mode, non-empty encoded transform metadata, valid compression/encryption identifiers, and normal write verification before calling `btrfs_do_write_iter()`.

io_uring encoded read/write support stores command-private data in the io_uring PDU. Encoded reads can return `-EAGAIN` for nonblocking reissue, or retain inode/extent locks until asynchronous fill-pages completion schedules task work that copies pages to the user iterator and releases locks.

## State and Synchronization
Uses `mnt_want_write_file()` / `mnt_drop_write_file()` around write-side ioctls, `subvol_sem` for subvolume/root flag changes, exclusive operation helpers for filesystem-wide operations, qgroup locks, balance mutex/lock, root/inode locks, extent locks, and transaction boundaries.

Subvolume creation/deletion interacts with dentries through `start_creating_killable()`, `end_creating()`, `start_removing_killable()`, and `end_removing()`. Balance transfers ownership of `btrfs_balance_control` and exclusive-op state to `btrfs_balance()` when execution starts.

## Risks
This file is a high-risk UAPI boundary. Correctness depends on strict user-copy sizing, compat layout conversion, capability checks, idmapped mount checks, transaction abort decisions, and exclusive-op lifecycle.

io_uring encoded read intentionally returns to userspace with inode/extent locks held and uses lockdep annotations to model the delayed unlock. Any missed cleanup path could leak locks, pages, iovecs, or command-private data.

Several operations copy progress/state back to userspace even on operation errors. That is intentional for scrub/balance style workflows, but callers must preserve the “operation failed but progress copy succeeded” distinction.
