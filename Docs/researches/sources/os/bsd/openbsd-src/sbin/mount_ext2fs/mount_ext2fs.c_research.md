# File Research: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/mount_ext2fs.c

`mount_ext2fs.c` mounts ext2 filesystems. It accepts shared `-o` options, resolves the mount point, fills a `struct ufs_args` with the device path and export info, and calls `mount(MOUNT_EXT2FS, ...)`.

The helper sets export flags to read-only when `MNT_RDONLY` is present. Error handling maps mount-table-full, device mismatch/update errors, unsupported kernel support, and generic errno into readable fatal messages.

The code is intentionally thin and delegates filesystem interpretation to the kernel.
