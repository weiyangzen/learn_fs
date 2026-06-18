# File Research: sources/os/linux/linux/fs/orangefs/orangefs-utils.c

## Role

OrangeFS utility glue between VFS inode state and OrangeFS userspace protocol state. It extracts filesystem IDs from queued operations, translates OrangeFS attributes and errors into Linux VFS forms, performs getattr/setattr upcalls, and detects stale cached inodes.

## Main Responsibilities

- `fsid_of_op()` maps each `ORANGEFS_VFS_OP_*` upcall type to the correct embedded `fs_id`, returning `ORANGEFS_FS_ID_NULL` for unknown or null operations.
- Permission and flag translation is centralized in `orangefs_inode_flags()`, `orangefs_inode_perms()`, `orangefs_inode_type()`, and `ORANGEFS_util_translate_mode()`.
- `copy_attributes_from_inode()` builds an `ORANGEFS_sys_attr_s` setattr mask from `ORANGEFS_I(inode)->attr_valid`, intentionally excluding size changes.
- `orangefs_inode_getattr()` implements cached getattr refresh, full/new inode initialization, stale-type checks, symlink target caching, uid/gid/time/mode setup, and timeout refresh.
- `orangefs_inode_setattr()` submits pending attribute updates via `ORANGEFS_VFS_OP_SETATTR`, clears the dirty attr mask, and marks non-root inodes bad on writeback failure.
- `orangefs_normalize_to_errno()` converts OrangeFS encoded negative status values into Linux `-errno`.

## Important Control Flow

`orangefs_inode_getattr()` first checks cached attributes under `i_lock`. If local attribute changes are pending, it forces `write_inode_now()` and retries. It skips server refresh when cached data is still valid or dirty pages could make size stale. When it does issue a GETATTR upcall, it may omit size unless full attributes are requested. Existing inodes are checked with `orangefs_inode_is_stale()` before applying returned data.

`orangefs_inode_is_stale()` treats type changes, unknown object types, and symlink target changes as stale and calls `orangefs_make_bad_inode()`. The root inode is protected from `make_bad_inode()` because losing root operations after userspace client restart would be fatal to the mount.

## Data and ABI Notes

The error mapping table mirrors OrangeFS/PVFS userspace errno ordering. Protocol errors with `ORANGEFS_NON_ERRNO_ERROR_BIT` are mostly collapsed to `-EINVAL`, except `ORANGEFS_ECANCEL`, which becomes `-ETIMEDOUT`.

## Dependencies

Uses operation allocation/service helpers from OrangeFS core, VFS inode state helpers, OrangeFS private inode data, and protocol constants from `protocol.h`.

## Research Notes

This file is the main consistency point for OrangeFS inode metadata. Any change to protocol object types, attr masks, error encoding, or pending attribute semantics must be reflected here.
