# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_args.h

Read completely: 39 lines.

This public mount-argument header defines `struct sysvbfs_args` with a single `char *fspec` field naming the block special device to mount.

Important interactions: `sysvbfs_mount` validates the provided data length, handles `MNT_GETARGS`, copies back no fspec string, and uses `fspec` through `namei_simple_user` for normal mounts.

Security/reliability notes: the only user/kernel boundary in this header is the device-path pointer. Runtime validation is in `sysvbfs_vfsops.c`.
