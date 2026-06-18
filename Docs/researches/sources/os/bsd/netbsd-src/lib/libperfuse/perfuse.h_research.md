# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.h

## Purpose
Public wrapper header for applications using `libperfuse` as a FUSE compatibility layer.

## Main Responsibilities
- Declares `perfuse_open()` and `perfuse_mount()`.
- When `LIBPERFUSE` is not defined, macro-replaces `mount()` and `open()` with perfuse wrappers.
- Keeps the wrapper small and independent of private perfuse internals.

## Dependencies
- Includes `sys/cdefs.h` and `sys/types.h`.
