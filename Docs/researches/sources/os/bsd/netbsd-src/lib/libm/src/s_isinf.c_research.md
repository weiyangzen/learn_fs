# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isinf.c

Implements double `isinf()` by checking for all-ones exponent and zero fraction.

Key behavior: returns 1 for either sign of infinity and 0 otherwise.

Important dependencies: `math_private.h` and `EXTRACT_WORDS`.

Notable risks: no branchless sign distinction; assumes IEEE double layout.
