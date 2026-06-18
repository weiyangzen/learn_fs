# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs.h

## Scope

This header defines SMBFS mount-level state, mount flags, statfs cache metadata, filesystem attribute info, and helper macros.

## APIs And Definitions

- `SMB_MAXFNAMELEN` defines component length excluding terminating null.
- Statfs cache constants and status bits cover busy, waiter, timeout, and dead mount states.
- Declares SMBFS vnodeops template and vnodeops pointer.
- Defines mount flags for interruptible operations, no attribute cache, local locking, ACL support, direct I/O, extended attributes, and dead mounts.
- `smb_fs_attr_info_t` stores filesystem attribute flags, maximum name length, and filesystem type name.
- `smbmntinfo_t` stores VFS pointer, root node, netsmb share, taskq, lock, flags/status, cached statvfs, FS attributes, per-mount node AVL tree, kstats, zone list membership, owner/group/mode defaults, and attribute cache timeout settings.
- Defines default and maximum attribute cache timeouts.
- Defines `SEC2HR()`, `VTOSMI()`, `VFTOSMI()`, and `SMBINTR()` helpers.

## Dependencies

- Used by all SMBFS vnode, mount, ACL, client, and protocol bridge code.
- Depends on VFS, AVL, taskq, zone, mount argument, and netsmb share types.

## Risks And Invariants

- `smi_hash_avl` is the per-mount node cache despite historical “hash” names.
- `smi_lock` protects flags/status; `smi_hash_lk` protects the node AVL.
- Cache timeout values are stored as high-resolution nanoseconds.
