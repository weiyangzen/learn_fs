# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockfs.h

## Role

Filesystem lock ioctl data structures and constants, historically used by UFS-style lockfs operations.

## Structure

Defines native `struct lockfs`, `_SYSCALL32` `struct lockfs32`, lock types from unlock through write/name/delete/hard/error/read-only-error lock, flags for busy and modified state, max comment length, and convenience macros to test/set/clear flags and lock type.

## Dependencies And Consumers

Relies on base illumos integer/pointer typedefs from including context. Kernel ioctl translation code uses `lockfs32` when supporting 32-bit applications in an LP64 kernel.

## Important Details

`LOCKFS_ROELOCK` is documented as unimplemented but still assigned a value and included in `LOCKFS_MAXLOCK`. The macros evaluate their `LF` argument multiple times only through pointer dereference expressions, so callers should pass stable pointers.

## Research Notes

Read completely: 101 lines, 3081 bytes.
