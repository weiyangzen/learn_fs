# File Research: sources/os/linux/linux-stable/fs/fuse/cuse.c

## Purpose
Implements CUSE, which lets a userspace server provide character devices through the FUSE request protocol.

## Key Interfaces
- Frontend device ops route `read_iter`, `write_iter`, `ioctl`, `poll`, `open`, and `release` through FUSE direct I/O and file operations.
- `cuse_channel_open()` opens `/dev/cuse`, allocates a `cuse_conn`, initializes an embedded FUSE connection, installs a FUSE device, and sends `CUSE_INIT`.
- `cuse_process_init_reply()` handles the daemon’s init reply, parses device metadata, reserves a character device number, creates the device, adds the cdev, and publishes it.
- `cuse_channel_release()` removes the device and releases the FUSE channel.
- Module init creates the `cuse` class and miscdevice.

## Design Notes
CUSE stores active connections in a hash table keyed by device number, protected by `cuse_lock`. Opening the created character device looks up the connection, takes a FUSE connection reference, and performs a FUSE open. The init info parser accepts packed NUL-separated key/value strings and currently requires `DEVNAME`.

## Dependencies
Uses FUSE device infrastructure, miscdevice, cdev, device model, user namespaces, direct I/O, ioctl support, and sysfs device attributes.

## Research Notes
The code explicitly disables `FUSE_DEV_IOC_CLONE` for CUSE. Device availability is announced only after the cdev and device are fully installed.
