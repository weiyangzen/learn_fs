# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_nanl.c

This file implements `nanl(const char *s)` for ld128.

It uses `_scan_nan()` to parse the payload string into four 32-bit words, then sets the long-double exponent to all ones and forces the quiet-NaN bit in `extu_frach`.

The representation is built through a union containing `union ieee_ext_u` and a `uint32_t bits[4]` view. It is small but architecture-format-sensitive through `math_private.h`.

Its only public behavior is returning a quiet long-double NaN with an optional payload.
