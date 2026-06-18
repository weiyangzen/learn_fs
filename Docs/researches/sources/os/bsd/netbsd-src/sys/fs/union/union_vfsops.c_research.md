# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_vfsops.c

Read completely: 588 lines.

Implements VFS operations and module registration for the legacy union filesystem. `union_mount()` validates mount arguments, supports `MNT_GETARGS`, rejects update remounts, resolves the target upper directory, chooses upper/lower ordering for `UNMNT_ABOVE`, `UNMNT_BELOW`, or `UNMNT_REPLACE`, checks whiteout support for writable mounts, stores mount credentials and shadow-directory mode, sets MPSAFE/local/readonly flags from underlying mounts, fills statvfs names, registers the lower mount, and installs the global union readdir hook when absent.

`union_unmount()` repeatedly flushes vnodes to account for parent references held by union nodes, optionally force-closes remaining vnodes, releases upper/lower roots and mount credentials, and frees `union_mount`. `union_root()` returns a union vnode over the mount roots using `union_allocvp()`. `union_statvfs()` combines lower used resources with upper totals/free resources, because only the upper layer is writable. `union_sync()` is a no-op because data is assumed to live in underlying layers. `union_vget()` and file-handle operations are unsupported. Rename locking delegates to the upper filesystem.

The `union_vfsops` table wires mount, root, unmount, statvfs, vnode cache loading, lifecycle hooks, suspend support, rename lock delegation, and vnode operation descriptors. Module init/fini attach and detach the VFS, and a sysctl node is registered under the historical VFS number 15.

Risks and notes: live update/remount is unsupported; NFS/file-handle support is not implemented; readonly state is copied from the upper layer at mount time and will not track later lower/upper remount changes; the sysctl number is hard-coded; and the global readdir hook is only installed if empty.
