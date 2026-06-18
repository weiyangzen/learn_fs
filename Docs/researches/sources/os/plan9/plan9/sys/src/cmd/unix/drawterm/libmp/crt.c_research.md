# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crt.c

Implements Chinese Remainder Theorem preprocessing and conversion.

Key functions:
- `crtpre`: copies moduli, computes cumulative products, and precomputes Garner coefficients.
- `crtprefree`: releases precomputed state.
- `crtin`: converts an integer to residues modulo each modulus.
- `crtout`: reconstructs an integer from residues using Garner’s algorithm.
- `crtresfree`: frees residue sets.

Important behavior:
- Uses `mpinvert`, `mpmul`, `mpmod`, `mpadd`, and `mpsub`.
- Based on Handbook of Applied Cryptography references in comments.
