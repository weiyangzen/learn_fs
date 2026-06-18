# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpexp.c

Exponentiation by repeated squaring, optionally modular.

Key function:
- `mpexp`: computes `b**e`, reducing modulo `m` when `m` is non-nil.

Important behavior:
- Handles output aliasing with base, exponent, or modulus by copying aliased operands.
- Skips the first high exponent bit before the main square/multiply loop.
- Periodically reduces intermediate values when larger than modulus.
