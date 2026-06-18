# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmul.c

Implements multiprecision multiplication.

Key functions:
- `mpkaratsuba`: recursive Karatsuba-like vector multiplication for large operands.
- `mpvecmul`: chooses Karatsuba above threshold or quadratic digit multiply-add.
- `mpmul`: signed `mpint` multiplication with alias handling and normalization.

Important behavior:
- `KARATSUBAMIN` is 32 limbs.
- Low-level multiplication depends on `mpvecdigmuladd`, `mpvecadd`, and `mpvecsub`.
- Product sign is the product of operand signs.
