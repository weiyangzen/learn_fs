# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs_impl.h

## Purpose

`objfs_impl.h` defines the internal objfs VFS/vnode object model. Objfs represents kernel modules and associated object data using generic filesystem (`gfs`) directory/file nodes and stable synthetic inode numbers.

## Main Structures

`objfs_vfs_t` stores the root vnode for a mounted objfs instance. The header declares common vnode operation helpers for directory open/access, common close, and common getattr, plus `objfs_nobjs()` for object count support.

Inode construction is defined by `OBJFS_INO(modid, type)`, which places a vnode type in the high 32 bits and the module ID in the low 32 bits. The root inode is `0xffffffff`. Module object directories use type 0, so their inode value equals the module ID.

The root node is a `gfs_dir_t`. Object directory nodes (`objfs_odirnode_t`) embed a `gfs_dir_t` and a `struct modctl *`. Data nodes (`objfs_datanode_t`) embed a `gfs_file_t`, an `objfs_info_t`, and a generation count captured when opened.

## Interfaces

The header declares operation templates and vnodeops pointers for root, object directory, and data file vnode types, plus constructors:

- `objfs_create_root(vfs_t *)`
- `objfs_create_odirnode(vnode_t *, struct modctl *)`
- `objfs_data_init()`
- `objfs_create_data(vnode_t *)`

## Research Notes

The file is internal and depends on `modctl`, VFS/vnode, GFS, and public objfs definitions. Correctness depends on synthetic inode stability, module generation handling for data files, and keeping GFS node embedding as the first struct member where expected by GFS helpers.
