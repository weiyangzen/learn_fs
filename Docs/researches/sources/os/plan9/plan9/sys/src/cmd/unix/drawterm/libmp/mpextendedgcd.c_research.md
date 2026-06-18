# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpextendedgcd.c

Binary extended GCD algorithm.

Key function:
- `mpextendedgcd`: computes `v = gcd(a,b)` and coefficients `x`, `y`.

Important behavior:
- Removes common factors of two first, tracked in `g`.
- Maintains coefficient pairs `(A,B)` and `(C,D)` while repeatedly halving even values and subtracting larger from smaller.
- Restores common power-of-two factor at the end.
