# File Research: sources/os/bsd/freebsd-src/sys/sys/libkern.h

Kernel libc-like utility header. It provides inline BCD/binary/hex conversion helpers with assertion bounds, min/max/abs variants for several integer types, random/ARC4 routines, timing-safe compare, bsearch, qsort/qsort_r, pattern matching, memory/string routines, and string duplication helpers.

Bit helpers wrap compiler builtins for first/last set bit, integer log2, power-of-two rounding, and bit counts. `ilog2()` chooses constant or generic forms using compiler features and `_Generic`.

It also handles sanitizer interceptors for selected string functions, defines `index`/`rindex`, signed-extension helpers for bitfields, `fnmatch` flags, and `__ssp_real` integration for user builds with SSP headers.
