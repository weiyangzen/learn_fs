# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_sinh.c

Implements no-IEEE `sinh`, `sinhf`, and aliases.

Key behavior:
- Reduces to positive magnitude and restores the original sign.
- For ordinary magnitudes, computes `(expm1(x) + expm1(x)/(1+expm1(x))) / 2`.
- Near overflow, subtracts a split `ln(2^(max+1))` and scales to avoid unnecessary overflow.
- For huge finite values, overflows through `expm1(x)*sign`.
- `sinhf` delegates to double `sinh`.

Special constants differ for VAX/Tahoe and IEEE-style targets.
