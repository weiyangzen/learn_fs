# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/milieu.h

This SoftFloat environment header includes `m68k-gcc.h` and defines boolean constants `FALSE` and `TRUE`. Most of the file is the upstream SoftFloat license and integration notice.

Its purpose is to provide common integer, endian, and boolean definitions before the architecture’s `softfloat.h` API declarations. There is no runtime logic.
