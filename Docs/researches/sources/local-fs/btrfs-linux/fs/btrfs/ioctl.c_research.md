# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.c

## Purpose

Implements the main Btrfs ioctl control plane plus file attribute integration and io_uring encoded I/O commands. This is the primary user-kernel interface for subvolume/snapshot operations, device management, balance/scrub/quota controls, tree and inode lookup queries, feature flags, labels, send/receive metadata, encoded reads/writes, sync controls, and forced shutdown.

## Main Responsibilities

- Maps VFS and Btrfs inode flags for `FS_IOC_GETFLAGS`/fileattr operations.
- Validates and applies mutable inode flags, including compression, no-COW, append, immutable, sync, noatime, and dirsynchronous flags.
- Handles subvolume and snapshot create/delete, readonly flag updates, default subvolume selection, root references, and subvolume sync wait operations.
- Provides tree search, inode-to-path, logical-to-inode, unprivileged inode lookup with permission checks, and subvolume metadata/rootref queries.
- Manages filesystem/device operations: resize, add/remove device, device replace, fs/device info, dev stats.
- Coordinates long-running exclusive operations: resize, device remove, balance, and device add interactions with paused balance.
- Runs defrag, trim, scrub, balance, quota/qgroup, quota rescan, and transaction sync ioctls.
- Supports send ioctl and receive metadata update through `SET_RECEIVED_SUBVOL`, including 32-bit compat layouts.
- Implements encoded read/write ioctl and io_uring command paths for encoded data streams.
- Dispatches all Btrfs-specific ioctl commands through `btrfs_ioctl()` and compat conversion through `btrfs_compat_ioctl()`.

## Key Behaviors and Invariants

- UAPI structs are copied with `memdup_user()`/`copy_from_user()` and string paths are NUL-checked before use.
- Most mutating operations require `CAP_SYS_ADMIN`, `mnt_want_write_file()`, and explicit readonly/root-state validation.
- Subvolume and snapshot creation reserve metadata and qgroup space before starting transactions; anon device ownership is carefully transferred to new roots.
- Snapshot creation forces future writes to COW and waits ordered extents before creating the snapshot.
- Subvolume deletion supports name-based and id-based v2 deletion; idmapped mount deletion by subvolid is deliberately restricted.
- Tree search copies results incrementally, pre-faults user buffers to avoid livelock, and preserves v1 overflow behavior.
- Balance, resize, remove, device replace, and device add rely on Btrfs exclusive-operation state to prevent conflicting long operations.
- Scrub copies progress back to userspace even on selected errors so userspace can resume.
- Received-subvolume UUID changes check UUID-tree overflow before transaction start to avoid user-triggered transaction aborts.
- Encoded I/O requires `CAP_SYS_ADMIN`; writes require `FMODE_WRITE` and reject invalid reserved fields, unsupported compression/encryption ids, and invalid unencoded ranges.
- io_uring encoded read may return to userspace with an inode lock held; lockdep handoff annotations are paired with task-work completion cleanup.

## Dependencies

Heavy dependencies include transaction handling, roots, qgroups, device management, block groups, scrub, send, compression, encoded I/O helpers, fsverity, locking helpers, and VFS permission/write-mount APIs.

## Research Notes

This file is a high-risk integration hub: correctness depends less on local algorithms and more on preserving ordering between permission checks, mount write acquisition, exclusive-operation state, transaction lifetime, root references, qgroup reservation, and userspace copy-back semantics.
