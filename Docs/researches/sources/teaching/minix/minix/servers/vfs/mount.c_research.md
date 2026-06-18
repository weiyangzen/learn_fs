# File Research: sources/teaching/minix/minix/servers/vfs/mount.c

Implements VFS mount and unmount lifecycle. Entry points are `do_mount`, `mount_fs`, `mount_pfs`, `do_umount`, `unmount`, and `unmount_all`.

Key behavior:
- `do_mount` validates superuser privilege, copies mount label/device/path/type from the caller, resolves the filesystem service endpoint through DS, translates the device path to a block device or allocates a `NONE_MAJOR` pseudo-device, then delegates to `mount_fs`.
- `mount_fs` allocates and locks a `vmnt`, checks duplicate mounted devices, resolves non-root mountpoints, calls `req_mountpoint`, allocates a root vnode, sends `REQ_READSUPER`, fills statvfs cache, and attaches root or non-root mounts into the global mount tree.
- Root mounting is special: `have_root` allows an initial ramdisk root and a later boot-disk root replacement. All processes' root and working directories are replaced with the new root vnode.
- `mount_pfs` mounts PipeFS as a pseudo filesystem with a `vmnt` entry for pipes and sockets.
- `unmount` refuses busy mounts by scanning vnode references and locks, cleans vnode references, sends `REQ_UNMOUNT`, frees pseudo-devices, marks the `vmnt` free, and reroutes block special file I/O back to `ROOT_FS_E`.
- `update_bspec` scans live block-special vnodes for a device and updates `v_bfs_e`, optionally sending `REQ_NEW_DRIVER` to the target filesystem.

Important dependencies:
- Path lookup through `lookup_init` and `eat_path`.
- Vnode/vmnt lifecycle through `get_free_vnode`, `get_free_vmnt`, `mark_vmnt_free`, locks, `put_vnode`.
- Request layer through `req_readsuper`, `req_mountpoint`, `req_unmount`, `req_newdriver`.
- Block-special-file serialization through `lock_bsf`.

Notable implementation details:
- Pseudo devices are tracked by a static bitmap and allocated lazily with `find_free_nonedev`.
- Non-root mounts temporarily unlock the parent `vmnt` before calling into FS to avoid back-call deadlocks.
- `unmount_all(force)` repeatedly scans all `vmnt` slots because mount dependencies require peeling mounts from leaves inward.
