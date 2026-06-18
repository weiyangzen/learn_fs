# File Research: sources/os/bsd/openbsd-src/sbin/mount_cd9660/mount_cd9660.c

`mount_cd9660.c` mounts ISO-9660 filesystems. It parses CD9660-specific flags for extended attributes (`-e`), generation numbers (`-g`), disabling Joliet (`-j`), disabling Rock Ridge (`-R`), and session selection (`-s`), plus shared `-o` options.

The helper resolves the mount point, fills `struct iso_args`, defaults export root to `-2`, forces `MNT_RDONLY`, sets export read-only state, and calls `mount(MOUNT_CD9660, ...)`.

Errors distinguish unsupported kernel filesystem support from other mount failures.
