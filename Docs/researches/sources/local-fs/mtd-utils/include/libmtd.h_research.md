# File Research: sources/local-fs/mtd-utils/include/libmtd.h

## Purpose
Public API for the `libmtd` user-space helper library.

## Key Elements
Defines `libmtd_t`, `struct mtd_info`, `struct mtd_dev_info`, and functions for opening/closing the library, discovering devices, querying geometry, locking/unlocking, erasing, bad-block handling, OOB I/O, data I/O, image writing, torture testing, and probing nodes.

## Dependencies
Depends on MTD ABI structs such as `region_info_user`; implementations are in the libmtd sources outside this group.

## Behavior/Risks
This is a thin abstraction over sysfs and MTD ioctls. Callers must still open device nodes and pass valid eraseblock indexes and offsets.
