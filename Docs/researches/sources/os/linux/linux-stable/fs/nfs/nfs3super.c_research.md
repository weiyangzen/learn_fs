# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3super.c

## Purpose
Registers NFSv3 support as an NFS subversion module.

## Main Behavior
- Defines exported `nfs_v3`:
  - owner: `THIS_MODULE`
  - filesystem type: `nfs_fs_type`
  - RPC version: `nfs_version3`
  - RPC ops: `nfs_v3_clientops`
  - superblock ops: `nfs_sops`
- `init_nfs_v3()` registers the subversion.
- `exit_nfs_v3()` unregisters it.
- Declares module description and GPL license.

## Research Notes
No protocol mechanics live here. It binds NFSv3 XDR/proc/client code into the common NFS version registry.
