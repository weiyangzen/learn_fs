# File Research: sources/os/bsd/freebsd-src/sys/sys/spigenio.h

## Purpose
`spigenio.h` defines ioctl structures and commands for the generic SPI device interface.

## Main Interfaces
- `struct spigen_transfer` describes command and data buffers using `struct iovec`.
- `struct spigen_transfer_mmapped` describes command and data lengths in an mmap-backed transfer area.
- Ioctls support normal and mmap transfers plus get/set operations for SPI clock speed and SPI mode.

## Implementation Notes
The command buffer is master-to-slave. The data buffer can be slave-to-master and/or master-to-slave. The mmap form places command data at offset 0 and transfer data immediately after it.

## Dependencies and Constraints
Includes `sys/_iovec.h`. The ioctl namespace uses base character `'S'`; consumers need ioctl macro definitions from their include context.
