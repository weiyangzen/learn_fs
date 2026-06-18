# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feenableexcept.c

Implements `feenableexcept`.

Key behavior:
- Reads current softfloat exception mask.
- Enables requested exceptions via `fpsetmask(omask | __FPE(excepts))`.
- Returns previous enabled exceptions using `__FEE`.
