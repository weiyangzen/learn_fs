# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.c

## Purpose
Registers V7FS with NetBSD as a VFS module and defines vnode operation vectors for regular, special, and FIFO nodes.

## Main Interfaces
- `v7fs_vnodeop_entries`, `v7fs_specop_entries`, and `v7fs_fifoop_entries` map VOP descriptors to V7FS, genfs, specfs, and fifofs handlers.
- `v7fs_vfsops` exposes mount, unmount, sync, vnode loading, statvfs, and root-mount entry points.
- `v7fs_genfsops` integrates the file system with genfs page-cache operations.
- `v7fs_modcmd()` attaches/detaches the file system module.

## Implementation Notes
Most unsupported operations use genfs error/default helpers. Device and FIFO vnodes share V7FS metadata operations but use spec/fifo read/write behavior.

## Dependencies
Depends on vnode/VFS declarations in `v7fs_extern.h`, genfs, specfs, fifofs, module infrastructure, and V7FS vnode/VFS operation implementations.
