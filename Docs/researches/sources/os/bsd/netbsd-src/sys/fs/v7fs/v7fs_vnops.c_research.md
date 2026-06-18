# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vnops.c

## Purpose
Implements NetBSD vnode operations for V7FS files, directories, symlinks, special nodes, metadata changes, page-cache I/O, directory reads, block mapping, locking, and reclamation.

## Main Interfaces
- Name operations: `v7fs_lookup()`, `v7fs_create()`, `v7fs_mknod()`, `v7fs_remove()`, `v7fs_link()`, `v7fs_rename()`, `v7fs_mkdir()`, and `v7fs_rmdir()`.
- Data operations: `v7fs_read()`, `v7fs_write()`, `v7fs_fsync()`, `v7fs_bmap()`, and `v7fs_strategy()`.
- Metadata operations: `v7fs_access()`, `v7fs_getattr()`, `v7fs_setattr()`, `v7fs_update()`, `v7fs_pathconf()`, and `v7fs_advlock()`.
- Directory/symlink operations: `v7fs_readdir()`, `v7fs_symlink()`, and `v7fs_readlink()`.
- Lifecycle operations: `v7fs_open()`, `v7fs_close()`, `v7fs_inactive()`, `v7fs_reclaim()`, and `v7fs_print()`.

## Implementation Notes
The vnode layer uses the core file helpers for namespace mutations and `uvm_vnp_setsize()` to keep vnode size synchronized with inode size. Reads/writes use `ubc_uiomove()` through the unified buffer cache. `v7fs_reclaim()` frees blocks and deallocates the inode when link count reaches zero. `v7fs_readdir()` synthesizes NetBSD `struct dirent` records from fixed V7 dirents and inode type lookup.

## Dependencies
Uses NetBSD VOP argument structures, genfs/UBC/buf/lockf/kauth APIs, and nearly all V7FS core helpers: file, dirent, inode, datablock, and mount structures.
