# File Research: sources/os/bsd/openbsd-src/sbin/mount_ffs/mount_ffs.c

`mount_ffs.c` mounts FFS/UFS filesystems. It accepts shared options plus FFS-relevant flags including `wxallowed`, `noperm`, `async`, `sync`, `update`, `reload`, `force`, and `softdep`.

After resolving the mount point, it fills `struct ufs_args`, sets export flags according to read-only state, expands `MNT_NOPERM` into `MNT_NODEV | MNT_NOEXEC`, and calls `mount(MOUNT_FFS, ...)`.

Errors get filesystem-specific messages for full mount table, unsupported kernel support, and read-only-required filesystems that may need fsck.
