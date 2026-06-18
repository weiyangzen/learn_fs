# File Research: sources/virtualization/libguestfs/daemon/blkdiscard.c

Wraps Linux block discard ioctls when available.

Key points:
- `do_blkdiscard` gets the full device size via `do_blockdev_getsize64`, opens the device writable, and issues `BLKDISCARD` over the full byte range.
- `do_blkdiscardzeroes` opens the device read-only and returns the boolean result of `BLKDISCARDZEROES`.
- Optional groups are only available when the relevant ioctl macros are defined.
- Comments intentionally defer sysfs discard-limit probing because virtio-scsi usually supports arbitrary discards.
