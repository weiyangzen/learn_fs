# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdigdiv.c

Divides a two-limb dividend by a one-limb divisor to estimate a quotient digit.

Key function:
- `mpdigdiv`: returns saturated all-ones quotient if overflow/divide-by-zero would occur; otherwise uses shifting/subtraction and final low division.

Used by Knuth-style long division in `mpdiv.c`.
