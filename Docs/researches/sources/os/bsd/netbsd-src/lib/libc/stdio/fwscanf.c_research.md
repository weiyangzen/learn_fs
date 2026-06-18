# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwscanf.c

Implements `fwscanf()` and `fwscanf_l()` as variadic wrappers over `vfwscanf()` and `vfwscanf_l()`. The file contains no parsing logic itself; it only initializes and finalizes the `va_list`.

It is part of the wide scanf public API surface and exposes the locale-specific weak alias `fwscanf_l -> _fwscanf_l`.
