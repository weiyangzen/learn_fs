# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utime.h

## Role

Defines the `utime(2)` timestamp update structure.

## Key Interfaces

- `struct utimbuf` contains access time `actime` and modification time `modtime` as `time_t`.
- `_SYSCALL32` defines kernel view `struct utimbuf32` using `time32_t`.

## Risk Notes

This is public syscall ABI. 32-bit compatibility layout must stay synchronized with `utime` syscall copyin handling.
