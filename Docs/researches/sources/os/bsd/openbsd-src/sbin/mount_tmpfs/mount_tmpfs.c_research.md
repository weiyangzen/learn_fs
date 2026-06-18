# File Research: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.c

`mount_tmpfs.c` mounts tmpfs filesystems. It parses root uid/gid/mode overrides, node limit (`-n`), size limit (`-s`), and shared mount options including `wxallowed` and `update`.

`mount_tmpfs_parseargs()` initializes `struct tmpfs_args`, parses scaled numeric size/node values with `scan_scaled()`, canonicalizes the mount point, warns when a relative path is adjusted, stats the mount point, and inherits root uid/gid/mode from it unless explicitly overridden.

`mount_tmpfs()` then calls `mount(MOUNT_TMPFS, ...)`. The file also exposes parsing and mounting functions separately through `mount_tmpfs.h`, making the parser testable/reusable.
