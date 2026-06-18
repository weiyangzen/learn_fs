# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_tanh.c

Implements no-IEEE `tanh` and `tanhf`.

Key behavior:
- Uses sign/magnitude reduction.
- For tiny values, returns `x` while trying to raise inexact for nonzero inputs.
- For `0 < |x| <= 1`, uses `-expm1(-2x) / (2 - (-expm1(-2x)))`.
- For `1 < |x| <= 22`, uses `1 - 2/(expm1(2x)+2)`.
- For large finite values, returns signed one with an inexact trigger.
- For infinities, returns signed one.
- `tanhf` delegates to double `tanh`.
