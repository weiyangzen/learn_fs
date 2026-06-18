# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/mp.h

Multiprecision integer interface used by libsec.

Key contents:
- Defines `mpint`, digit sizing constants, static flag, allocation/normalization/copy APIs, random/conversion APIs, arithmetic, modular arithmetic, comparisons, extended GCD, modular inverse, bit counting, vector digit helpers, magnitude helpers, and CRT residue/precompute structures.
- Declares well-known constants `mpzero`, `mpone`, and `mptwo`.

Role in this group:
- Supplies big-integer contracts for RSA, DSA, ElGamal, prime generation, and related cryptographic code.

Notable risks:
- Assumes `mpdigit` is an atomic type and at least an int, as provided by architecture-specific compatibility headers.
