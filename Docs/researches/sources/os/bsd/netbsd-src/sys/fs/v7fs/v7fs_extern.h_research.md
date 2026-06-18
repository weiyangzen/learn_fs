# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.h

## Purpose
Defines the NetBSD-facing V7FS mount/node wrappers and declares VFS/VOP entry points.

## Main Interfaces
- `struct v7fs_mount` connects a NetBSD mount and device vnode to the core `struct v7fs_self`.
- `struct v7fs_node` embeds `genfs_node`, stores the V7FS inode, vnode back-pointer, advisory-lock state, and deferred timestamp flags.
- `VFSTOV7FS()` casts `mnt_data`.
- Declares vnode operations, VFS prototypes, operation vector pointers, genfs hooks, and `v7fs_update()`.

## Dependencies
Includes V7FS on-disk/core headers plus genfs and specfs declarations.
