# File Research: sources/os/linux/linux/fs/btrfs/ioctl.c

This file implements the Btrfs ioctl control plane, VFS file attribute integration, and Btrfs-specific io_uring encoded I/O commands. It is the primary userspace entry point for subvolume/snapshot operations, device management, balance/scrub/quota controls, tree and inode lookup queries, feature flags, labels, send metadata, encoded reads/writes, transaction sync, and forced shutdown.

Core responsibilities:
- Map Btrfs inode flags to/from VFS `FS_IOC_GETFLAGS`/fileattr flags, including compression, no-COW, immutable, append, sync, noatime, dirsync, and verity state.
- Create, snapshot, delete, query, and sync subvolumes.
- Expose tree-search, inode-to-path, logical-to-inode, subvolume-info, and rootref lookup ioctls.
- Manage filesystem devices: resize, add, remove, device info, filesystem info, dev stats, and device replace.
- Coordinate exclusive operations for resize, device removal, device replace, device add, and balance.
- Run defrag, trim, scrub, balance, quota/qgroup, quota rescan, and transaction sync operations.
- Get/set filesystem label and supported/active feature flags.
- Bridge `BTRFS_IOC_SEND`, received-subvolume metadata updates, and 32-bit compat UAPI layouts.
- Implement encoded read/write via traditional ioctl and io_uring command paths.
- Dispatch all Btrfs-specific ioctl commands through `btrfs_ioctl()` and compat remapping through `btrfs_compat_ioctl()`.

Important behavior:
- UAPI structs are copied with `memdup_user()`/`copy_from_user()` and path/name buffers are explicitly NUL-checked.
- Mutating operations generally require `CAP_SYS_ADMIN` or owner checks, `mnt_want_write_file()`, root readonly checks, and transaction handling.
- File flag changes reject unsupported or conflicting combinations such as compression plus NOCOW; zoned filesystems reject `FS_NOCOW_FL`.
- Compression fileattr changes update the `btrfs.compression` property inside the same transaction as inode flag updates.
- Subvolume creation reserves metadata/qgroup space before transaction work and carefully transfers anon device ownership to the new root.
- Snapshot creation forces future writes to COW, waits ordered extents, and commits through a pending snapshot transaction path.
- Subvolume deletion supports name-based v1/v2 and id-based v2 deletion; idmapped mount deletion by subvolid is deliberately restricted.
- Tree search copies results incrementally, faults user buffers before copying to avoid livelock, and preserves v1 overflow behavior.
- Received-subvolume UUID updates check UUID-tree item overflow before starting a transaction to avoid user-triggered transaction aborts.
- Scrub copies progress back to userspace even on selected errors so userspace can resume.
- Encoded I/O requires `CAP_SYS_ADMIN`; encoded writes require write mode and reject invalid reserved fields, unsupported compression/encryption ids, and inconsistent unencoded ranges.
- io_uring encoded reads may return to userspace with the inode lock held; lockdep annotations transfer cleanup to task-work completion.

Major internal areas:
- `btrfs_fileattr_get()` / `btrfs_fileattr_set()` implement VFS file attribute support.
- `create_subvol()`, `create_snapshot()`, `btrfs_mksubvol()`, and `btrfs_mksnapshot()` implement subvolume and snapshot creation.
- `btrfs_ioctl_snap_destroy()` implements subvolume deletion policy and dispatch.
- `search_ioctl()` plus `copy_to_sk()` implement tree-search ioctls.
- `btrfs_search_path_in_tree*()` implement privileged and permission-checked inode path lookup.
- Device operations call into `volumes.c`, `dev-replace.c`, scrub, and exclusive-operation helpers.
- Balance and quota ioctls call into the balance and qgroup subsystems while preserving mount write and locking order.
- Encoded ioctl/io_uring paths call `btrfs_encoded_read()`, `btrfs_encoded_read_regular*()`, and `btrfs_do_write_iter()`.

Cross-file relationships:
- Public prototypes are declared in `ioctl.h`.
- Uses locking helpers from `locking.h`, ordered extent waiting from ordered-data paths, qgroup metadata/data reservation APIs, transaction APIs, root-tree APIs, send support, scrub, device replacement, compression, defrag, uuid-tree, and fsverity.
- The io_uring encoded read endio callback is exported for compressed/encoded read completion integration.

Risk notes:
- This is a high-risk integration hub. Correctness depends on ordering among permission checks, mount write acquisition, exclusive-op state, transaction lifetime, root references, qgroup reservation conversion/freeing, user copy-back semantics, and inode/extent locking.
- Compat UAPI layouts are hand-translated and must stay byte-compatible with userspace structures.
