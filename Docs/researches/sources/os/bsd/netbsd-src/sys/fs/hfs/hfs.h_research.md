# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs.h

## Purpose
Defines the NetBSD HFS/HFS+ kernel-facing mount, vnode, callback, and helper interfaces.

## Main Contents
- `struct hfs_args` carries the device path supplied to mount.
- `struct hfsmount` links the VFS mount, device vnode, device id, and `hfs_volume` parsed by `libhfs`.
- `struct hfsnode_key` identifies cached vnodes by CNID and fork type.
- `struct hfsnode` stores the vnode, mount pointer, device vnode, catalog record, parent CNID, fork key, and genfs node.
- Callback argument structs pass credentials, lwps, and device vnodes into `libhfs`.
- Kernel macros convert mount/vnode pointers, fetch allocation block size, and convert HFS raw device numbers.
- Declares HFS vnode op descriptors, mount/VFS functions, vnode lookup helpers, callback wrappers, byte-order readers, and time conversion helpers.

## Dependencies
Includes NetBSD vnode/mount/genfs headers and `fs/hfs/libhfs.h`.

## Risks and Notes
Defaults for uid, gid, file mode, and directory mode are compile-time constants, not mount options. Comments mark `HFS_DEBUG`, default permissions, and several helper APIs as development-era or incomplete. `hfsnode` caches parent CNID at vnode creation, which would need update support if write/move operations were ever implemented.
