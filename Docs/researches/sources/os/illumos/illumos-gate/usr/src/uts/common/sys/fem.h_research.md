# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fem.h

## Purpose

`fem.h` defines the kernel File Event Monitoring framework for vnode and VFS operation interception. It lets filesystem consumers install monitor stacks that wrap vnode/VFS operations and forward to the next operation in the chain.

## Main Types

`femarg_t` / `fsemarg_t` carry the current vnode, vnode pointer, VFS, or anonymous argument plus the current `fem_node`.

`fem_t` describes a vnode operation monitor: name, operation template, and full `FEM_OPS` function table.

`fsem_t` describes a VFS operation monitor: name, operation template, and full `FSEM_OPS` function table.

`struct fem_node` holds monitor/private available data, a union of FEM/vnode/FSEM/VFS operation pointers, and optional hold/release callbacks for the available data.

`struct fem_list` is a reference-counted stack of monitor nodes.

`struct fem_head` owns the monitor list under a mutex.

`femhow_t` controls install policy: `FORCE`, `OPUNIQ`, or `OPARGUNIQ`.

## Interfaces

`FEM_OPS` mirrors the vnode operation surface: open, close, read, write, ioctl, setattr/getattr, lookup/create/remove/link/rename, directory operations, symlink/readlink, fsync, inactive, fid, rwlock, locking, page operations, mmap operations, poll, dump, pathconf, security attributes, share locks, vnode events, and zero-copy buffer operations.

`FSEM_OPS` mirrors VFS operations: mount, unmount, root, statvfs, sync, vget, mountroot, freevfs, vnstate, and syncfs.

`vnext_*` routines continue from a FEM monitor to the next vnode operation. `vfsnext_*` routines continue from a FSEM monitor to the next VFS operation.

Management routines include `fem_init()`, `fem_create()`, `fem_free()`, `fem_install()`, `fem_is_installed()`, `fem_uninstall()`, `fem_getvnops()`, `fem_setvnops()`, and the analogous `fsem_*` routines.

## Research Notes

This is a core filesystem extension point. It supports NFS delegation behavior, SMB filesystem event interception, portfs hooks, and common VFS/vnode interception. Monitor lists are copy/reconfigured stacks, so modules cannot assume a fixed list identity after installation.
