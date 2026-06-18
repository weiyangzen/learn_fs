# File Research: sources/os/linux/linux/fs/nfs/nfs3super.c

## Purpose
Registers and unregisters NFSv3 client support as a module-level NFS subversion.

## Main Behavior
- Defines exported `nfs_v3` with owner, core `nfs_fs_type`, `nfs_version3`, `nfs_v3_clientops`, and `nfs_sops`.
- `init_nfs_v3()` registers the subversion.
- `exit_nfs_v3()` unregisters it.

## Research Notes
This is module glue. NFSv3 behavior lives in `nfs3proc.c`, `nfs3xdr.c`, `nfs3client.c`, and optional `nfs3acl.c`.
