# File Research: sources/teaching/os161/kern/include/device.h

Defines the VFS-visible device abstraction.

Key structures:
- `struct device` contains ops, block count, block size, device number, and private data.
- `struct device_ops` provides each-open validation, `devop_io`, and ioctl.

Key APIs:
- `DEVOP_EACHOPEN`, `DEVOP_IO`, `DEVOP_IOCTL`.
- Device vnode creation/destruction helpers.
- Built-in device and bootstrap functions.

Relevance:
- SFS mounts on `struct device` and performs all disk block reads/writes through `DEVOP_IO`.
