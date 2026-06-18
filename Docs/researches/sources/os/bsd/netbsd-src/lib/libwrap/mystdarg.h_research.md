# File Research: sources/os/bsd/netbsd-src/lib/libwrap/mystdarg.h

## Purpose
Compatibility macro layer over ANSI `stdarg.h` and old `varargs.h`.

## Key Details
- Under `__STDC__`, uses `stdarg.h`.
- Otherwise uses `varargs.h`.
- Defines:
  - `VARARGS`
  - `VASTART`
  - `VAEND`

## Dependencies and Role
- Historical portability shim for tcp_wrappers code.
