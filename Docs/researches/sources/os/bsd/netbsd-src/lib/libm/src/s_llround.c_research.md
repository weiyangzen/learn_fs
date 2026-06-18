# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_llround.c

Macro instantiation wrapper for `llround(double)`. It uses `round()` and the shared `s_lround.c` template.

Key behavior: sets `DTYPE_MIN/MAX` to `LLONG_MIN/MAX`.

Important dependencies: `s_lround.c`, `round`, and `<limits.h>` through the template.

Notable risks: out-of-range handling is inherited from the template.
