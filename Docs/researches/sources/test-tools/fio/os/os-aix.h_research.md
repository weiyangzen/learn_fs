# sources/test-tools/fio/os/os-aix.h

## Purpose
`os-aix.h` selects fio's AIX platform capabilities and supplies inline OS helpers for direct I/O, anonymous mapping, block-device sizing, physical memory detection, and thread affinity discovery.

## Important APIs, Types, and Functions
It defines `FIO_OS os_aix`, `FIO_HAVE_ODIRECT`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `OS_MAP_ANON`, `OS_MSG_DONTWAIT`, and `FIO_USE_GENERIC_SWAP`. Inline helpers are `blockdev_invalidate_cache()`, `blockdev_size()`, and `os_phys_mem()`.

## Control Flow
`blockdev_size()` issues `ioctl(fd, IOCINFO, &devinfo)` and computes bytes from SCSI disk block count and block size. `os_phys_mem()` reads `_SC_AIX_REALMEM` via `sysconf()` and converts KiB to bytes. Cache invalidation is unsupported and returns `ENOTSUP`.

## State and Persistence
There is no persistent state. Calls query kernel/device state and report capability through compile-time macros.

## Dependencies and Integration Points
The header depends on AIX `<sys/devinfo.h>`, `<sys/ioctl.h>`, `unistd`, and fio's `file.h`. It feeds common fio file/device sizing, memory sizing, random seed initialization, byte swapping, and options that require direct I/O support.

## Risks and Edge Cases
`blockdev_size()` assumes the device reports `info.un.scdk` fields; non-disk devices may fail or report incompatible union members. `_SC_AIX_REALMEM` failure returns zero physical memory, which affects keyword substitution and memory-derived options.

## Test Signals
AIX build coverage, block-device size checks against known disks, `$mb_memory` keyword validation, and direct-I/O option smoke tests provide useful signals.
