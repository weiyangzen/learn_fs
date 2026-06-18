# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrl.c

## Scope

Long-double helper routines for complex trig functions.

## APIs And Behavior

- `_cchshl` computes long-double `coshl` and `sinhl`, using an `expl` split form outside `|x| <= 0.5`.
- `_redupil` reduces by nearest integer multiple of `M_PIL` using split long-double constants.
- `_ctansl` evaluates a long-double Taylor series for `cosh(2y) - cos(2x)`.
- VAX builds set `DP3 = 0` and use a looser `MACHEPL`.

## Dependencies And Risks

- Uses `long long` for the multiple in `_redupil`; very large inputs can exceed practical integer range.
- Constants and tolerance are architecture-sensitive.
