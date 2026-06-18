# File Research: sources/os/linux/linux-stable/fs/nfs/namespace.c

## Purpose
Implements NFS namespace behavior: path reconstruction, server-side mountpoint crossing, referrals/submounts, automount expiry, and the module parameter controlling automount timeout.

## Path Reconstruction
- `nfs_path(char **p, struct dentry *dentry, char *buffer, ssize_t buflen, unsigned flags)`
  - Reconstructs an NFS server path from a dentry chain and the root dentry's `d_fsdata`.
  - Uses `rename_lock` sequence checking plus RCU and dentry locks to retry safely during renames.
  - Supports `NFS_PATH_CANONICAL` to ensure a single slash between export root and relative path.
  - Returns `ERR_PTR(-ENAMETOOLONG)` if the buffer is too small.
- `nfs_devname()` in `internal.h` wraps this for canonical device/source naming.

## Automount and Submount
- `nfs_d_automount(struct path *path)`
  - Creates a submount fs_context from the parent mount.
  - Copies credentials and network namespace from the parent server/client.
  - Inherits selected superblock flags covered by `NFS_SB_MASK`.
  - Sets server address/version/minorversion/module from the parent client.
  - Optionally inherits block size.
  - Calls protocol-specific `submount()` operation, then creates a vfsmount.
  - Adds the mount to the NFS automount expiry list if timeout is positive.
- `nfs_submount(struct fs_context *fc, struct nfs_server *server)`
  - Re-lookups the mountpoint to obtain attributes and file handle.
  - Sets selected auth flavor from the parent server client.
  - Calls `nfs_do_submount()`.
- `nfs_do_submount(struct fs_context *fc)`
  - Clones the server using protocol-specific `clone_server()`.
  - Builds the source string with `nfs_devname()`.
  - Parses it into fs_context and calls `vfs_get_tree()`.

## Mountpoint and Referral Inode Ops
- `nfs_mountpoint_inode_operations`
  - Uses normal `nfs_getattr` and `nfs_setattr`.
- `nfs_referral_inode_operations`
  - Uses wrappers that fall back to generic attributes and reject setattr with `-EACCES` when the referral object has no file handle.

## Automount Expiry
- Global `nfs_automount_list` and delayed work `nfs_automount_task`.
- `nfs_expire_automounts()` calls `mark_mounts_for_expiry()` and reschedules while the list is non-empty.
- `nfs_release_automount_timer()` cancels delayed work when no automounts remain.
- `nfs_mountpoint_expiry_timeout` defaults to `500 * HZ`.

## Module Parameter
- `param_set_nfs_timeout()` parses seconds, converts to jiffies, reschedules expiry work, or disables expiry for non-positive values.
- `param_get_nfs_timeout()` reports seconds or `-1` when disabled.
- Exposed as `nfs_mountpoint_expiry_timeout`.

## Research Notes
This file is central to correct NFS behavior when a server export contains mountpoints or v4 referrals. It preserves identity and statistics by creating client-side mountpoints at server-side filesystem boundaries.
