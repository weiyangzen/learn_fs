# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gfs.h

## Role

`gfs.h` defines the Generic Filesystem helper layer used by in-kernel pseudo-filesystems that need vnode-backed synthetic files and directories.

## Key Interfaces and Data

- `gfs_opsvec_t` groups vnode operation templates and output `vnodeops_t **` values for registration via `gfs_make_opsvec()`.
- `gfs_dirent_t` describes a synthetic directory entry, optional constructor, flags, dynamic-list link, and cached vnode.
- `GFS_CACHE_VNODE` enables caching of constructed vnodes.
- `gfs_file_t` is generic vnode private data: current vnode, parent, size, type, index, and inode.
- `gfs_dir_t` embeds `gfs_file_t` and adds static entries, dynamic entry lock, max name length, and callbacks for readdir, lookup, and inode generation.
- Creation helpers allocate file, directory, root directory, and root file vnodes.
- Inactive helpers return private storage for cleanup.
- Directory lookup/read helpers implement generic case-sensitive/case-insensitive lookup and `readdir`.
- Macros provide directory locking and generic file parent/index/inode access.
- `gfs_readdir_state_t` tracks directory emission state, including dirent buffer, exported record size, original residual, parent/self inodes, and flags.
- Readdir helper functions emit `.`/`..`, named entries, numeric entries, and final EOF/residual state.
- Generic VOP entry points are declared for lookup, readdir, map, and inactive.

## Dependencies and Use

The header is consolidation-private and includes vnode, VFS operation registration, mutex, dirent, extended dirent, uio, list, and pathname types.

## Research Notes

GFS is a reusable pseudo-filesystem substrate. It centralizes vnode allocation, synthetic directory enumeration, and common VOP behavior so small pseudo-filesystems can provide only callbacks and static entry tables.
