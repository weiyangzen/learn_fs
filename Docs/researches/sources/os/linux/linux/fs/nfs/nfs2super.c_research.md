# File Research: sources/os/linux/linux/fs/nfs/nfs2super.c

## Purpose
Registers and unregisters NFSv2 client support as a module-level NFS subversion.

## Main Behavior
- Defines static `nfs_v2` with owner, core `nfs_fs_type`, `nfs_version2`, `nfs_v2_clientops`, and `nfs_sops`.
- `init_nfs_v2()` registers the subversion.
- `exit_nfs_v2()` unregisters it.

## Research Notes
This is module glue. The behavioral implementation for NFSv2 lives primarily in shared client code and `nfs2xdr.c`.
