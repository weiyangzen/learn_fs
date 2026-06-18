# File Research: sources/local-fs/jfsutils/libfs/devices.h

Public prototypes and constants for libfs device I/O.

Key contents:
- Includes `<stdint.h>`.
- Defines operation modes `GET`, `PUT`, and `VRFY`.
- Defines open-mode constants `READONLY` and `RDWR_EXCL`.
- Defines Windows-style error code constants used across jfsutils.
- Forward-declares `struct stat`.
- Declares `ujfs_get_dev_size()`, `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, and `ujfs_device_is_valid()`.

Interactions:
- Included by `devices.c`, `extract.c`, and other disk-access modules.

Research notes:
- `VRFY` is declared but `ujfs_rw_diskblocks()` only implements GET/PUT in this file.
