# File Research: sources/os/bsd/openbsd-src/sys/sys/mtio.h

Defines magnetic tape ioctl ABI.

Key contents:
- `struct mtop` for tape operations and count.
- Tape operations such as write EOF, forward/back file/record, rewind, offline, erase, end-of-media, cache control, block-size and density settings.
- `struct mtget` status with type, device status/error registers, residual, file/block numbers, block size, density, defaults.
- Tape device type constants and status bits.
- Ioctls `MTIOCTOP`, `MTIOCGET`, `MTIOCIEOT`, `MTIOCEEOT`, position read, and locate commands.
- Kernel minor-device bit macros for unit, no-rewind, and density selection.

Risk notes:
- Position ioctls use 32-bit logical/hardware block addresses and the file notes future SCSI SSC limitations.
