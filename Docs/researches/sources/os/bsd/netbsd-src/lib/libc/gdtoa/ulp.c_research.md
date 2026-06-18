# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ulp.c

Implements gdtoa internal `ulp(U *x)` for doubles.

Behavior:
- Computes the unit in the last place for the magnitude/exponent of `x`.
- Uses `word0`, `word1`, `Exp_mask`, `P`, `Exp_msk1`, and related gdtoa macros from `gdtoaimp.h`.
- Handles gradual underflow unless `Sudden_Underflow` is defined.
- Has IBM-format conditional exponent adjustment.

Role: low-level floating-point spacing helper used by gdtoa conversion algorithms.
