# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lrand.c

This file implements Plan 9's pseudo-random number generator.

Key behavior:
- `srand` seeds the generator.
- `lrand` returns 31-bit pseudo-random values using a lagged table after initialization.
- `isrand` initializes internal state using Park-Miller constants.

Important details:
- Table length is 607 with tap 273.
- `frand`, `nrand`, `lnrand`, and `rand` build on this generator.
