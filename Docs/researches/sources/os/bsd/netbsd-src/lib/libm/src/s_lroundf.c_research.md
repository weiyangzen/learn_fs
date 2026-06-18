# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lroundf.c

Macro instantiation wrapper for `lroundf(float)`.

Key behavior: uses `roundf()` and returns `long`, with `LONG_MIN/MAX` bounds.

Important dependencies: `s_lround.c` and `roundf`.

Notable risks: all range and exception behavior comes from the template.
