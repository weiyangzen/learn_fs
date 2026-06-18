# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrintl.c

Macro instantiation wrapper for `lrintl(long double)`.

Key behavior: uses `rintl()` and returns `long` through the shared `s_lrint.c` template.

Important dependencies: `s_lrint.c` and `rintl`.

Notable risks: assumes long-double `rintl()` availability.
