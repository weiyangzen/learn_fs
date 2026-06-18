# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmod.c

Computes positive modular remainder.

Key function:
- `mpmod`: calls `mpdiv` for remainder, then adds modulus back if the remainder is negative.

Used by modular exponentiation, CRT, inverse, and related arithmetic.
