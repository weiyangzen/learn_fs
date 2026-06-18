# File Research: sources/teaching/minix/minix/drivers/storage/vnd/vnd.c

## Purpose

Implements the MINIX vnode disk driver, exposing a regular file as a block device with partitions, geometry, read-only mode, and vnconfig-style ioctls.

## Main Entry Points

- `main()`: initializes SEF and enters `blockdriver_task()`.
- `vnd_init()`: initializes instance number and empty device state.
- `vnd_open()` / `vnd_close()`: validate configured state, enforce read-only access, reparse partitions, and manage open count.
- `vnd_transfer()`: reads/writes the backing file through an intermediate buffer and caller grants.
- `vnd_ioctl()`: handles `VNDIOCSET`, `VNDIOCCLR`, `VNDIOCGET`, `DIOCOPENCT`, and `DIOCFLUSH`.
- `vnd_layout()`: computes device geometry and accessible size from file size or user-provided geometry.
- `vnd_partition()` / `vnd_part()` / `vnd_geometry()`: maintain and expose partition/geometry data.
- `vnd_signal()`: defers termination until open count reaches zero.

## Control Flow And State

Global `state` stores the backing file descriptor, open count, exiting flag, read-only flag, backing file dev/inode, partition arrays, geometry, and 64 KiB transfer buffer. `VNDIOCSET` requires an unconfigured device with only the ioctl opener active, copies the caller's file descriptor into the driver using `copyfd()`, verifies it is a regular file, allocates the transfer buffer with `mmap()`, records read-only and identity state, computes layout, parses partitions, and returns the device size. `VNDIOCCLR` closes and unmaps the backing file, refusing if busy unless forced.

Transfers compute a bounded byte count within the selected partition, then chunk through the intermediate buffer. Reads use `pread()` followed by safe copy to the caller. Writes safe-copy from the caller, then `pwrite()` to the backing file. `BDEV_FORCEWRITE` triggers `fsync()`.

## Dependencies

Depends on MINIX blockdriver/drvlib APIs, partition parsing, `copyfd()` VFS backcall, safe-copy vector APIs, POSIX file operations, `mmap()`, and vnode disk ioctl structures from system headers.

## Risks

The device cannot recover after crash or live restart because it cannot reacquire the backing file descriptor. Forced clear closes the backing file while other opens may still exist, leaving the device unconfigured for later operations. `fsync()` return values are ignored. Intermediate-buffer copy logic is bounded by `VND_BUF_SIZE` and assumes `SCPVEC_NR >= NR_IOREQS`.
