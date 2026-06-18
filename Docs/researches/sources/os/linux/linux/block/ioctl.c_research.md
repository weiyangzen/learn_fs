# File Research: sources/os/linux/linux/block/ioctl.c

Implements generic block-device ioctls, compat ioctl handling, persistent reservation ioctls, partition add/delete/resize ioctls, discard/secure erase/zeroout, and a block io_uring command for discard.

Key responsibilities:
- Validates user ranges, alignment, permissions, and device capabilities.
- Handles partition table manipulation through `BLKPG`.
- Implements discard, secure discard, and zeroout after invalidating relevant page-cache ranges.
- Provides common geometry, size, block-size, read-only, readahead, zone, crypto, trace, and persistent reservation ioctls.
- Falls back to driver-specific `fops->ioctl` / `compat_ioctl` when generic handling returns `-ENOIOCTLCMD`.
- Implements `BLOCK_URING_CMD_DISCARD`.

Important functions:
- `blkpg_do_ioctl()` validates and dispatches add/delete/resize partition operations.
- `blk_validate_byte_range()` centralizes byte-range validation.
- `blk_ioctl_discard()`, `blk_ioctl_secure_erase()`, `blk_ioctl_zeroout()` implement destructive range operations.
- `blkdev_common_ioctl()` handles generic native/compat-compatible commands.
- `blkdev_ioctl()` and `compat_blkdev_ioctl()` handle ABI-specific commands.
- `blkdev_pr_*()` wrappers implement persistent reservation operations.
- `blkdev_bszset()` changes soft block size, using exclusive open if needed.
- `blkdev_uring_cmd()` supports async discard via io_uring command.

Concurrency/lifetime notes:
- Destructive range operations take inode and invalidate locks before truncating cache and issuing device operations.
- Persistent reservation operations are denied on partitions and gate unprivileged access by open mode.
- Nonblocking io_uring discard rejects multi-bio cases with `-EAGAIN` to avoid hidden partial errors.

Research relevance:
- This file defines much of the userspace administrative ABI for block devices.
