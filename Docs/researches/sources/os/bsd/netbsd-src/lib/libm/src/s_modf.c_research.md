# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modf.c

Implements double `modf()`, splitting a value into fractional and integral parts by bit masking.

Key behavior: returns signed fractional zero for integral inputs, stores signed integral zero for `|x| < 1`, handles Inf/NaN specially, and raises no exceptions intentionally.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, and `INSERT_WORDS`.

Notable risks: IEEE double layout and signed-zero handling are central.
