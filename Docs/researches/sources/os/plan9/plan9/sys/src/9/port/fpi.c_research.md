# File Research: sources/os/plan9/plan9/sys/src/9/port/fpi.c

Purpose: Software floating-point interpreter arithmetic over the internal representation defined in `fpi.h`.

Key logic:
- `fpiround` implements guard-bit rounding with carry propagation.
- `matchexponents`, `shift`, `normalise`, and `renormalise` align and normalize operands/results.
- `fpiadd`, `fpisub`, `fpimul`, and `fpidiv` implement IEEE-like addition, subtraction, multiplication, and division with NaN/infinity/zero handling.
- `fpicmp` compares internal floating values, including signed zero, infinities, and NaNs.
- Note in file warns `fpisub` and `fpidiv` argument order computes `y-x` and `y/x`.

Dependencies and integration:
- Uses only `fpi.h`; designed as portable arithmetic support where hardware floating point is absent or trapped.

Risks and notes:
- Internal precision uses two 28-bit chunks plus guard bits.
- Some weird cases intentionally return quiet NaN.
