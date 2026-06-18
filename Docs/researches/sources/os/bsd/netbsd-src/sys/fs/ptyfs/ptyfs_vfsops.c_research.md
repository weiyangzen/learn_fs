# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vfsops.c

Implements ptyfs VFS operations and hooks pty allocation/name generation into the kernel pty subsystem.

Key points:
- Defines module and `ptyfs_vfsops` for `MOUNT_PTYFS`.
- Maintains a global list of ptyfs mounts and a mount count.
- Installs `ptm_ptyfspty` as the active pty handler on first mount and restores the previous handler on last unmount.
- ptm glue:
  - `ptyfs__getmp()` selects a ptyfs mount visible from the caller’s root.
  - `ptyfs__getpath()` computes a mount path adjusted for chroot visibility.
  - `ptyfs__makename()` returns `/dev/null` for master-side names and mount-relative numeric slave paths for active slaves, with fallback to previous handler where appropriate.
  - `ptyfs__allocvp()` creates ptyfs vnodes for master/slave pty device requests and marks controlling ptys active.
  - `ptyfs__getvattr()` supplies ownership/mode defaults for new pty nodes.
- Mount flow:
  - Validates versioned `ptyfs_args`.
  - Handles `MNT_GETARGS`.
  - Rejects update mounts.
  - Allocates `ptyfsmount`, initializes lock and active bitmap state, sets local mount flag and statvfs info, inserts into global mount list, and hooks pty handler.
- Unmount:
  - Flushes vnodes, restores previous pty handler if this was the last ptyfs mount, removes mount from list, frees bitmap, destroys lock, and frees mount data.
- Vnode loading:
  - `ptyfs_loadvnode()` maps keys to root directory or character-device vnodes using `spec_node_init()`.
- Unsupported:
  - `ptyfs_vget()` returns `EOPNOTSUPP`.
  - File handles, snapshots, extattrs, and VFS fsync are unsupported.
- Creates a VFS sysctl node for `ptyfs`.

Role:
- This file is the mount/control-plane side of ptyfs; actual file operation behavior is in the ptyfs vnode layer outside this grouped file list.
