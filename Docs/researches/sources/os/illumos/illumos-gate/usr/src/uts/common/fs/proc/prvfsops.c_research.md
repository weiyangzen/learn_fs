# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvfsops.c

## Purpose

`prvfsops.c` implements the VFS/module layer for procfs. It registers the `proc` filesystem type, creates mount root nodes, handles mount/unmount/root/statvfs operations, and assigns per-mount pseudo-device identifiers.

## Module Registration

- `_init()` installs the filesystem module via `mod_install()`.
- `_info()` returns module information via `mod_info()`.
- There is deliberately no `_fini()`; the procfs module cannot be unloaded once loaded.

The `vfsdef_t` advertises the filesystem as `proc` with flags including protocol support, stats, extended IDs, and zone mount support.

## Initialization

`prinit()` is called by the VFS framework for the filesystem type. It:

- Computes `nproc_highbit`.
- Stores the procfs type ID.
- Registers VFS operations with `vfs_setfsops()`.
- Builds vnode operations with `vn_make_ops()`.
- Gets a unique major number with `getudev()`.
- Initializes mount and minor-number locks.

`prinitrootnode()` allocates and initializes a root `prnode_t` and vnode. The root vnode is a directory marked `VROOT`, `VNOCACHE`, `VNOMAP`, `VNOSWAP`, and `VNOMOUNT`, uses `prvnodeops`, and has procfs node type `PR_PROCDIR` with mode `0555`.

## Mount

`prmount()` enforces mount policy and mountpoint validity:

- Requires `secpolicy_fs_mount()`.
- Requires the mountpoint vnode to be a directory.
- In the global zone, verifies the mount path belongs to the global zone.
- Forces the VFS resource string to `"proc"`.
- Rejects busy non-overlay mountpoints.
- Allocates a procfs root `prnode_t`.
- Assigns filesystem type, root data, block size, and a unique pseudo-device minor number.
- Builds the VFS fsid.

Mount serialization is protected by `pr_mount_lock`; minor assignment is protected by `procfs_minor_lock`.

## Unmount

`prunmount()`:

- Requires `secpolicy_fs_unmount()`.
- Rejects forced unmounts with `ENOTSUP`.
- Fails with `EBUSY` if the root vnode is still referenced.
- Invalidates and frees the root vnode.
- Frees the root `prnode_t`.

## Root and Statvfs

`prroot()` returns a held reference to the procfs root vnode.

`prstatvfs()` fills `statvfs64` with pseudo-filesystem values:

- Block counts are zero.
- File count is based on configured process slots plus two.
- Free file counts are based on configured process slots minus current process count.
- fsid is derived from the procfs pseudo-device.
- base type and filesystem string are `/proc`.
- name maximum is fixed at 64.

## Dependencies

This file anchors procfs into the illumos VFS/module framework and depends on procfs vnode operations declared elsewhere through `prvnodeops` and `pr_vnodeops_template`. Its root nodes become the directory entry point for the rest of procfs.
