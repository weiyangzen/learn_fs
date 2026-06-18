# File Research: sources/os/linux/linux-stable/fs/quota/quotaio_v1.h

## Purpose
Defines old-format VFS quota on-disk record layout and constants.

## Contents
- `MAX_IQ_TIME` and `MAX_DQ_TIME`: default inode and block grace times, both one week.
- `struct v1_disk_dqblk`: old quota record with 32-bit block/inode limits and current usage plus architecture-sized `unsigned long` timers.
- `v1_dqoff(UID)`: computes byte offset of a record by ID.

## Role
Consumed by `quota_v1.c` for direct array-style quota file reads and writes.
