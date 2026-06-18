# File Research: sources/os/bsd/freebsd-src/sys/sys/statvfs.h

## Purpose
`statvfs.h` defines the POSIX `statvfs` filesystem capacity/status interface.

## Main Interfaces
- Defines `fsblkcnt_t` and `fsfilcnt_t`.
- `struct statvfs` exposes block counts, file counts, block size, flags, fragment size, filesystem ID placeholder, and maximum name length.
- Defines `ST_RDONLY` and `ST_NOSUID`.
- Declares `statvfs()` and `fstatvfs()`.

## Implementation Notes
The comments distinguish `f_bavail` from `f_bfree`: available space for unprivileged callers versus all free space, including privileged reserves.

## Dependencies and Constraints
Includes `sys/cdefs.h` and `sys/_types.h`. The interface maps filesystem data into POSIX unsigned count types.
