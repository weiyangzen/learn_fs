# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecdigmuladd.c

Contains single-digit multiply helpers for limb-vector arithmetic: static `mpdigmul`, public `mpvecdigmuladd`, and public `mpvecdigmulsub`. It splits an `mpdigit` into high and low half-digits using `LO` and `HI` macros to compute a two-limb product without requiring a wider native type.

`mpvecdigmuladd(b, n, m, p)` adds `m * b[0:n-1]` into `p[0:n]`, carrying through the extra digit. `mpvecdigmulsub(b, n, m, p)` subtracts the same product from `p[0:n]` and returns `1` for nonnegative final subtraction or `-1` when the high digit underflows.

The file is central to multiplication/division-style `mpint` internals. Preconditions require `p` to have room for `n+1` digits; the code mutates `p` in place and does not normalize.
