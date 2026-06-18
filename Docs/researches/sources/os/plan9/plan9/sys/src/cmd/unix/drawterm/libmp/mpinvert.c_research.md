# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpinvert.c

Computes modular multiplicative inverses.

Key function:
- `mpinvert`: uses `mpextendedgcd` to find inverse of `b mod m`, aborts if gcd is not one, then normalizes result with `mpmod`.

Important behavior:
- Allocates temporary throwaway gcd/coefficient values and frees them.
