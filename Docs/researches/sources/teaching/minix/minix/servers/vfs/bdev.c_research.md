# File Research: sources/teaching/minix/minix/servers/vfs/bdev.c

This file handles VFS-side block device open, close, ioctl, reply processing, and block-driver recovery notification.

Key functions:
- `bdev_sendrec`: sends a block-driver request and waits for a reply using `drv_sendrec`.
- `bdev_open`: opens a block device with translated read/write access bits.
- `bdev_close`: closes a block device.
- `bdev_ioctl`: creates an ioctl grant, sends `BDEV_IOCTL`, revokes grant, and returns driver status.
- `bdev_reply`: routes asynchronous block-driver replies back to the waiting worker thread.
- `bdev_up`: reopens open block-special files and informs mounted filesystems after block-driver remapping/restart.

Important behavior:
- Block drivers may not suspend requests, so VFS blocks the current worker thread until completion.
- `ERESTART` replies are retried up to five times; persistent restart failure becomes `EIO`.
- Dead driver endpoints are unmapped from `dmap` and converted to `EIO`.
- `bdev_up` notifies mounted filesystems with `req_newdriver` using the recovered driver label.
- If any block-special file was open, the root FS is also informed about the new driver.
