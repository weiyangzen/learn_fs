# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_nanl.c

Implements `nanl(const char *s)` for 80-bit long double. It scans a NaN payload string into raw words, sets the ld80 exponent to all ones, and forces the quiet-NaN bits in the high fraction word.

Key behavior:
- Uses `_scan_nan(u.bits, 3, s)` to parse payload bits.
- Writes the exponent and quiet bit through `union ieee_ext_u`.
- Returns the constructed `long double` NaN.

Important dependencies: `fpmath.h`, `../src/math_private.h`, and `_scan_nan`.

Notable risks:
- Assumes the three-word storage arrangement used by NetBSD/FreeBSD ld80 support.
