# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/pftest.c

Printf-format test program using `stdio1.h` and gdtoa conversion routines.

Behavior:
- Maintains a current printf format string, default `"%.g"`.
- Lines beginning with `%` update the format and infer type mode: double, long double/extended, or quad where available.
- Parses subsequent numeric text with `strtod`, `strtopx`, or `strtopQ` depending on architecture and mode.
- Prints raw representation and then applies the requested printf format.

Architecture conditionals handle x86_64, i386, sparc, Intel compiler exclusions, and optional `__float128` quad support.
