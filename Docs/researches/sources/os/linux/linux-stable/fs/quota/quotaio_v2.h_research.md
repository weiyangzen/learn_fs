# File Research: sources/os/linux/linux-stable/fs/quota/quotaio_v2.h

## Purpose
Defines VFS quota v2 on-disk constants and structures.

## Contents
- `V2_INITQMAGICS`: magic numbers for user, group, and project quotas.
- `V2_INITQVERSIONS`: current version values, all `1`.
- `struct v2_disk_dqheader`: file magic and version.
- `struct v2r0_disk_dqblk`: v0 quota record with 32-bit limit/count fields where applicable.
- `struct v2r1_disk_dqblk`: v1 quota record with 64-bit limits/counts.
- `struct v2_disk_dqinfo`: grace times, flags, block count, free block list head, and free-entry block list head.
- `V2_DQINFOOFF`: info header offset after the generic header.
- `V2_DQBLKSIZE_BITS`: quota tree block size shift, 10.

## Role
Used by `quota_v2.c` and `quota_tree.c` to interpret and maintain v2 quota files.
