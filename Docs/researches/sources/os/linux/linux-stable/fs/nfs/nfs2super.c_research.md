# File Research: sources/os/linux/linux-stable/fs/nfs/nfs2super.c

## Purpose
Registers NFSv2 support as an NFS subversion module.

## Main Behavior
- Defines static `nfs_v2`:
  - owner: `THIS_MODULE`
  - filesystem type: `nfs_fs_type`
  - RPC version: `nfs_version2`
  - RPC ops: `nfs_v2_clientops`
  - superblock ops: `nfs_sops`
- `init_nfs_v2()` registers the subversion.
- `exit_nfs_v2()` unregisters it.
- Declares module description and GPL license.

## Research Notes
No protocol logic lives here; it is a module registration shim binding the v2 XDR/proc implementation to the common NFS client.
