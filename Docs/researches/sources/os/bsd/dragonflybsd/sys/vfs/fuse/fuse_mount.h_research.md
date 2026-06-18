# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_mount.h

Defines mount argument flags and the userspace-to-kernel mount info structure for FUSE.

Flags are `FUSE_MOUNT_DEFAULT_PERMISSIONS`, `FUSE_MOUNT_ALLOW_OTHER`, `FUSE_MOUNT_MAX_READ`, and `FUSE_MOUNT_SUBTYPE`. `struct fuse_mount_info` contains flags, the `/dev/fuse` fd, max read size, optional subtype string, and source/from string.

Important dependencies: `fuse_vfsops.c` copies this structure from userspace during mount and uses `fd`, `from`, and optional `subtype`. Several flags are defined but not fully acted on in the listed `fuse_vfsops.c`.

Notable risks or research hooks: string pointers are userspace pointers consumed through `copyinstr`; future flag implementation should verify permission semantics such as `allow_other` and `default_permissions`.
