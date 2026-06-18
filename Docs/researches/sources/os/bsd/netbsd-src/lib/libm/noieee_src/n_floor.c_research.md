# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_floor.c

Implements legacy `floor`, `ceil`, `rint`, `lrint`, `llrint`, float variants, and `trunc` variants. The core technique adds and subtracts a large power of two to force rounding to an integer.

Key behavior:
- `floor()` and `ceil()` use volatile temporaries to force storage rounding.
- Negative cases delegate to the opposite function with sign negation.
- `rint()` uses `copysign(L, x)` to round according to the current rounding mode.
- Integer-returning `lrint*`/`llrint*` use the same large-add technique and return the converted result.
- `trunc()` chooses `ceil()` for negative and `floor()` for nonnegative values.

Important dependencies: `mathimpl.h`, `copysign()`, and weak aliases for long-double names where long double matches double.

Notable risks:
- The implementation intentionally raises inexact for non-integer inputs.
- Returning `x` from `lrint`/`llrint` on NaN or huge values depends on implicit conversion behavior.
