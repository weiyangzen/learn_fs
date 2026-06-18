# File Research: sources/os/bsd/openbsd-src/sbin/mount_msdos/mount_msdos.c

`mount_msdos.c` mounts FAT/MS-DOS filesystems. It parses name-mode flags (`-s`, `-l`, `-9`), uid/gid/mask overrides, and shared mount options.

If uid/gid/mask are omitted, it inherits them from the mount point’s existing stat data. User and group arguments can be names or numeric IDs validated with `strtonum()`, and masks are parsed as octal modes.

The helper fills `struct msdosfs_args`, sets export root to `-2`, sets read-only export flags when needed, and calls `mount(MOUNT_MSDOS, ...)`. It reports unsupported kernel support, full mount table, and invalid FAT filesystem errors distinctly.
