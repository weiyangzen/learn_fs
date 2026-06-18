# File Research: sources/os/linux/linux/fs/nfs/namespace.c

## Purpose
Implements NFS namespace handling: reconstructing server-side paths, automounting server-side mountpoints/referrals, expiring automounts, and creating submounts when crossing filesystem boundaries.

## Key Functions
- `nfs_path()` reconstructs a server pathname from an arbitrary dentry, using `rename_lock` sequence retry plus dentry locking, and optionally canonicalizes slash handling after the export name.
- `nfs_d_automount()` creates a submount fs_context, inherits credentials/net namespace/superblock flags from the parent, prepares clone data, invokes the protocol-specific submount operation, creates a vfsmount, and schedules expiry.
- `nfs_namespace_getattr()` / `nfs_namespace_setattr()` handle referral-like dentries with empty file handles specially.
- `nfs_expire_automounts()` marks automounts for expiry and reschedules while the list is non-empty.
- `nfs_do_submount()` clones the server, computes a source string with `nfs_devname()`, parses it into the fs_context, and gets the tree.
- `nfs_submount()` redoes lookup to refresh mountpoint attributes, selects the auth flavor, and calls `nfs_do_submount()`.

## Inode Operations
- `nfs_mountpoint_inode_operations` uses normal NFS getattr/setattr and wires `fileattr_get = nfs_fileattr_get`.
- `nfs_referral_inode_operations` uses namespace-specific getattr/setattr and also wires `fileattr_get = nfs_fileattr_get`.

## Module Parameter
`nfs_mountpoint_expiry_timeout` controls automount expiry in seconds. Values `<= 0` disable expiration; setter converts to jiffies and updates/cancels delayed work.

## Research Notes
The subtle parts are path reconstruction under concurrent rename, fs_context inheritance for submounts, active automount expiry management, and special referral dentries that may not carry a real file handle.
