# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtol.c

Instantiates the shared `_strtol.h` signed integer parser for `long`. It defines `_FUNCNAME` as `strtol`, `__INT` as `long`, and the `LONG_MIN`/`LONG_MAX` bounds before including the template.

All parsing behavior lives in `_strtol.h`; this file binds the template to the public `strtol()` type.
