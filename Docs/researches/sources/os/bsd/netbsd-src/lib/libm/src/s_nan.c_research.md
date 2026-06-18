# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nan.c

Implements `nan()` and `nanf()` payload construction and shared `_scan_nan()`.

Key behavior: parses optional `0x`-prefixed hex payload strings, fills payload words according to host endianness, discards high-order overflow bits, and forces quiet-NaN exponent/significand bits.

Important dependencies: `<sys/endian.h>`, `<ctype.h>`, `<stdint.h>`, `math_private.h`, and byte-order macros.

Notable risks: comment notes compatibility limits with C standard and gdtoa `hexnan.c`; payload layout is endian-sensitive.
