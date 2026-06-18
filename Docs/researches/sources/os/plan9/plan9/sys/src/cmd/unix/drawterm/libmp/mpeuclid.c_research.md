# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpeuclid.c

Classic extended Euclidean algorithm.

Key function:
- `mpeuclid`: computes `d = gcd(a,b)` plus coefficients `x`, `y` such that `ax + by = d`.

Important behavior:
- Swaps inputs and output coefficient targets if needed so `a >= b`.
- Iteratively divides and rotates coefficient state.
- Copies inputs before mutation and frees temporaries at the end.
