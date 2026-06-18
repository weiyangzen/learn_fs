# File Research: sources/local-fs/mtd-utils/lib/libmtd_int.h

## Purpose
Defines libmtd-private constants, sysfs filename fragments, 64-bit ioctl support states, the internal `struct libmtd`, and prototypes for legacy fallback functions.

## Main Definitions
- Sysfs constants cover `/sys/class/mtd/mtd%d` and attribute files used by `libmtd.c`.
- `OFFS64_IOCTLS_UNKNOWN`, `OFFS64_IOCTLS_NOT_SUPPORTED`, and `OFFS64_IOCTLS_SUPPORTED` describe lazy probing state for 64-bit erase/OOB ioctls.
- `struct libmtd` stores path templates for sysfs reads and bitfields for sysfs and 64-bit ioctl support.

## Dependencies
Includes `libmtd.h` indirectly through users of the prototypes and provides C++ linkage guards for internal functions.

## Risks and Notes
The header documents why 64-bit ioctl support is discovered later rather than during `libmtd_open()`: probing requires a real MTD device file descriptor.
