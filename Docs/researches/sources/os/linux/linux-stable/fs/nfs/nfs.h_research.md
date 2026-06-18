# File Research: sources/os/linux/linux-stable/fs/nfs/nfs.h

## Purpose
Internal interface exported by the base NFS module for version-specific NFS modules.

## Main Type
- `struct nfs_subversion`
  - Holds module owner, filesystem type, RPC version table, protocol operation table, superblock operations, and xattr handlers for one NFS protocol version.

## Declared API
- `find_nfs_version(unsigned int)`
- `get_nfs_version(struct nfs_subversion *)`
- `put_nfs_version(struct nfs_subversion *)`
- `register_nfs_version(struct nfs_subversion *)`
- `unregister_nfs_version(struct nfs_subversion *)`

## Research Notes
This is the version registration contract used by `nfs2super.c`, `nfs3super.c`, and NFSv4 module code.
