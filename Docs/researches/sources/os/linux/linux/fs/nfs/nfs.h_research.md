# File Research: sources/os/linux/linux/fs/nfs/nfs.h

## Purpose
Defines `struct nfs_subversion`, the registration object used by NFS version-specific modules, and declares version lookup/reference management APIs.

## Main Interfaces
- `struct nfs_subversion` contains module owner, filesystem type, RPC version table, client operation table, super operations, and xattr handlers.
- `find_nfs_version()`, `get_nfs_version()`, `put_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()` manage available NFS protocol versions.

## Research Notes
This header is the narrow contract between the core NFS module and version modules such as NFSv2 and NFSv3.
