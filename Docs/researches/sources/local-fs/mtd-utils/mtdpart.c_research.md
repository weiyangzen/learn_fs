# File Research: sources/local-fs/mtd-utils/mtdpart.c

## Purpose
Adds or deletes MTD partitions through the block partitioning ioctl interface.

## Key Elements
Parses `add <MTD_DEVICE> <PART_NAME> <START> <SIZE>` and `del <MTD_DEVICE> <PART_NUMBER>`. Builds `blkpg_partition` and `blkpg_ioctl_arg`, then issues `BLKPG_ADD_PARTITION` or `BLKPG_DEL_PARTITION`.

## Dependencies
Uses `linux/blkpg.h`, getopt, POSIX open/close, and `common.h` parsing/error helpers.

## Behavior/Risks
Requires an `O_RDWR` MTD device and kernel support for `BLKPG`. The tool validates negative numbers and partition-name length, but relies on the kernel to reject invalid alignment, overlap, or device-specific partition constraints.
