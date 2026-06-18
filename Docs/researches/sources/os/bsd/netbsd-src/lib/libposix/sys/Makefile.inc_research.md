# File Research: sources/os/bsd/netbsd-src/lib/libposix/sys/Makefile.inc

## Purpose
Generates syscall wrapper stubs for `libposix`.

## Main Responsibilities
- Adds `.PATH` entries for generic and architecture syscall sources.
- Generates pseudo assembly stubs for `chown`, `fchown`, `lchown`, and `rename`, each calling the corresponding `__posix_*` symbol.
- Builds `cerror.S` with `__cerror` remapped to `__posix_cerror`.
- Defines dependencies on `SYS.h` and generated syscall headers.
- Generates lint stubs when lint is enabled.

## Dependencies
- libc object directory, architecture `SYS.h`, `sys/syscall.h`, libc `makelintstub`.
