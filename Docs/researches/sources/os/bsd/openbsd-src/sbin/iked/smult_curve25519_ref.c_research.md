# File Research: sources/os/bsd/openbsd-src/sbin/iked/smult_curve25519_ref.c

This is a compact public-domain Curve25519 scalar multiplication reference implementation derived from Matthew Dempsky and D. J. Bernstein code.

Key responsibilities:
- Exposes `crypto_scalarmult_curve25519(q, n, p)`.
- Clamps the scalar, loads the peer point, runs a Montgomery ladder, computes a field inverse, multiplies to affine form, freezes modulo `2^255 - 19`, and writes the 32-byte shared secret.
- Implements field operations over 32 byte-limb arrays: `add`, `sub`, `squeeze`, `freeze`, `mult`, `mult121665`, `square`, and `recip`.
- `select` performs branchless conditional selection for ladder state.
- `mainloop` executes the scalar ladder from bit 254 down to bit 0.

Security and correctness notes:
- The implementation uses fixed-size loops and branchless conditional swap/selection for scalar-dependent choices.
- It is reference-style, not optimized assembly.
- No allocation, file I/O, or OS interactions occur.
