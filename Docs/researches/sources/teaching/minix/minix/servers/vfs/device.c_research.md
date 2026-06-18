# File Research: sources/teaching/minix/minix/servers/vfs/device.c

Device-type-independent ioctl support.

Key functions:
- `do_ioctl`: VFS syscall handler for `ioctl(2)`.
- `make_ioctl_grant`: creates a magic grant for an ioctl buffer.

`do_ioctl` behavior:
- Gets and locks the file descriptor’s filp.
- Dispatches by vnode type:
  - block device: `bdev_ioctl`
  - character device: `cdev_io(CDEV_IOCTL, ...)`
  - socket: `sdev_ioctl`
  - other: `ENOTTY`
- Temporarily marks `filp_ioctl_fp` for block-device ioctl deadlock protection used by remote FD copying.
- Unlocks the filp before returning.

`make_ioctl_grant` behavior:
- Derives copy direction and size from MINIX ioctl encoding.
- Supports regular and BIG ioctl size encodings.
- Creates a `cpf_grant_magic` for driver access and panics if grant creation fails.
