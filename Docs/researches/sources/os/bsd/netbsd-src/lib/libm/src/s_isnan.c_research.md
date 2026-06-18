# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_isnan.c

Implements double `isnan()` with branchless bit tests.

Key behavior: folds low-word nonzero state into the high word, compares absolute representation against infinity, and returns 1 only for NaNs.

Important dependencies: `math_private.h` and `EXTRACT_WORDS`.

Notable risks: relies on unsigned wraparound and IEEE double encoding.
