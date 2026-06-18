# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundl.c

Macro instantiation wrapper for `lroundl(long double)`.

Key behavior: includes `s_lround.c` with `roundl()` and `long` output.

Important dependencies: `s_lround.c`, `roundl`, and `LONG_MIN/MAX`.

Notable risks: template range logic is sensitive for long double to integer conversions.
