# File Research: sources/os/linux/linux/fs/nfs/nfs42.h

## Purpose
Declares NFSv4.2 client procedure interfaces and helper constants.

## Main Interfaces
Under `CONFIG_NFS_V4_2`, declares procedure helpers for allocate, copy, deallocate, zero range, llseek, layoutstats, clone, layouterror, copy notify, getxattr, setxattr, listxattr, and removexattr.

## Helpers
- `PNFS_LAYOUTSTATS_MAXDEV` caps layoutstats devices per compound.
- `READ_PLUS_SCRATCH_SIZE` defines scratch sizing.
- `nfs42_files_from_same_server()` compares server owner major IDs for copy/clone decisions.
- `nfs42_listxattr_xdrsize()` estimates listxattr XDR buffer size for a requested output size and rounds to 4-byte alignment.

## Research Notes
This header is declarative but important for v4.2 feature gating. The listxattr sizing helper encodes assumptions about worst-case user xattr name packing.
