# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vfsops.c

Read completely: 222 lines.

Implements MFS VFS operations by mounting an FFS instance over a kernel vnode whose backing store is a user-process memory region.

Core behavior:
- `mfs_vfsops` reuses many FFS/UFS operations: unmount, root, quota, statfs, sync, vget, file-handle conversion, sysctl, and generic UFS root/export helpers where appropriate.
- `mfs_mount()` handles update mounts, read-only transitions, optional export update, creates a `VT_MFS` block vnode, assigns a synthetic device number, allocates `struct mfsnode`, records memory base/size and servicing thread id, initializes the buffer queue, then calls `ffs_mountfs()`.
- After mount, it fills `fs_fsmnt`, `mnt_stat.f_mntonname`, `f_mntfromname`, `f_mntfromspec`, and stored MFS args.
- `mfs_start()` keeps the mounting process in-kernel as an I/O server: drains queued buffers through `mfs_doio()`, sleeps on the device vnode, and on signals tries to unmount, forcing only for `SIGKILL`.
- `mfs_checkexp()` rejects exports with `EOPNOTSUPP`; `mfs_init()` delegates to `ffs_init()`.

Integration and risks:
- The filesystem lives only while the server process and memory mapping are valid.
- Signal/unmount handling is delicate; failed unmounts clear the pending signal to avoid spinning.
- Duplicate synthetic device aliases panic.
