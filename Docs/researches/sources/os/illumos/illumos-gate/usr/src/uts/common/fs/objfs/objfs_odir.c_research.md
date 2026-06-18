# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_odir.c

## Purpose
Implements each per-module objfs directory `/system/object/<module>`, containing the synthetic `object` file.

## Main Entry Points
- `objfs_create_odirnode()` creates a GFS directory vnode for one loaded module and records its `modctl`.
- `objfs_odir_do_inode()` derives the inode number for the contained `object` file.
- `objfs_odir_getattr()` reports read/execute directory attributes.
- `objfs_tops_odir[]` registers object-directory VOPs.

## Internal Mechanics
The directory entries table contains a single real entry: `"object"`, created by `objfs_create_data()`. Inode numbers are generated from the module id with `OBJFS_INO_DATA()`. Attributes are dynamic timestamps from `gethrestime()` plus common objfs fields.

## Dependencies
Uses GFS directory helpers, objfs inode macros, module control structures, and common objfs directory/access helpers.

## Risks and Notes
The object-directory vnode stores a raw persistent `modctl` pointer. The data file later validates the underlying module generation before exposing contents.
