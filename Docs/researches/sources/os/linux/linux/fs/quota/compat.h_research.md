# File Research: sources/os/linux/linux/fs/quota/compat.h

## Role

Defines 32-bit compatibility structures for quota ioctls on compat tasks.

## Structures

- `struct compat_if_dqblk`: compat layout for quota block/inode limits, current usage, timers, and validity mask.
- `struct compat_fs_qfilestat`: compat layout for quota file statistics.
- `struct compat_fs_quota_stat`: compat layout for filesystem quota state, including version, flags, user/group quota file stats, in-core dquot count, time limits, and warning limits.

## Dependencies

Includes `<linux/compat.h>` for fixed compat integer types.

## Research Notes

This header contains ABI layout definitions only. It is consumed by quota ioctl compatibility code outside this grouped file list.
