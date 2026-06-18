# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vfsops.c

## Purpose
Implements NetBSD VFS operations for mounting, unmounting, syncing, statvfs, vnode loading, root lookup, module lifecycle, and root-file-system mounting.

## Main Interfaces
- `v7fs_mount()` validates mount arguments/device vnode, authorizes access, opens the block device, and calls `v7fs_mountfs()`.
- `v7fs_mountfs()` allocates `struct v7fs_mount`, initializes core I/O, loads the superblock, and fills mount metadata.
- `v7fs_unmount()` flushes vnodes, closes the device, tears down V7FS core state, and clears mount data.
- `v7fs_sync()` writes the superblock and fsyncs allocated live vnodes selected by `v7fs_sync_selector()`.
- `v7fs_loadvnode()` loads a V7 inode into a pooled `struct v7fs_node`, initializes genfs state, sets vnode type/op vector, and handles special/FIFO nodes.
- `v7fs_vget()`, `v7fs_root()`, `v7fs_statvfs()`, `v7fs_init()`, `v7fs_done()`, and `v7fs_mountroot()` provide standard VFS integration.

## Implementation Notes
`v7fs_mode_to_vtype()` maps V7 mode bits to vnode types. File handles are not implemented (`EOPNOTSUPP`). Root mounting verifies the disk wedge type is `DKW_PTYPE_V7`.

## Dependencies
Uses NetBSD mount, vnode cache, genfs, specfs, pools, authorization, disk wedge, and V7FS core I/O/superblock/inode code.
