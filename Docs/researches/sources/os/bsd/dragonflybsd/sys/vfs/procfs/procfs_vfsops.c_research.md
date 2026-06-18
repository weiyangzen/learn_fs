# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vfsops.c

This file implements procfs VFS operations. `procfs_mount()` rejects update mounts, registers `procfs_exit` as an exit hook when needed, marks the mount local, non-stackable, and quick-halt, assigns a new fsid, sets `f_mntfromname` to `procfs`, initializes statfs, and installs vnode ops.

`procfs_unmount()` flushes vnodes and unregisters the exit hook when the last procfs mount goes away. `procfs_root()` allocates the synthetic root vnode. `procfs_statfs()` reports page-sized block/io sizes, one block, and approximate file counts from `maxproc` and `nprocs`.

The module is registered with `VFCF_SYNTHETIC | VFCF_MPSAFE`.

Research notes: procfs has no backing storage; VFS state is almost entirely synthetic and tied to live process state.
