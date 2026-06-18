# File Research: sources/os/bsd/openbsd-src/sbin/mount_ntfs/mount_ntfs.c

`mount_ntfs.c` mounts NTFS filesystems. It parses case-insensitive lookup (`-i`), all-names exposure (`-a`), uid/gid/mode overrides, and shared mount options.

The helper always adds `MNT_RDONLY`, inherits uid/gid/mode from the mount point when not provided, fills `struct ntfs_args`, sets export root to 65534, and calls `mount(MOUNT_NTFS, ...)`.

User/group parsing accepts names or numeric IDs. Mode parsing is octal. The implementation is thin and mostly prepares kernel mount arguments.
