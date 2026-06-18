# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfprintf.c

Builds the narrow `vfprintf` implementation by defining `NARROW` and including `vfwprintf.c`. This shared-source pattern makes `vfwprintf.c` compile both narrow and wide printf engines through type and helper macros.

The only direct declaration here is the weak alias `vfprintf_l -> _vfprintf_l`.
