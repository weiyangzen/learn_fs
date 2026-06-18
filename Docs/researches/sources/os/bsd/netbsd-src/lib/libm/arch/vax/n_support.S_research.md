# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_support.S

## Scope

Implements assorted VAX libm support functions: `copysign`, `copysignf`, `logb`, `logbf`, `finite`, `isnanf`, `scalb`, and `drem`.

## APIs And Behavior

- `copysign*` copy the sign of the second argument to the first unless the first is zero or a reserved operand.
- `logb` extracts and unbiases the VAX D exponent; zero returns a sentinel `-2147483647.0`, reserved operand returns itself. `logbf` promotes/delegates.
- `_finite` returns false only for the reserved operand encoding; VAX `isnanf` always returns false.
- `scalb` converts the second double argument to an integer exponent adjustment, checks range, adjusts the exponent field, underflows to zero, or calls `infnan(ERANGE)` on overflow.
- `drem` implements IEEE-style remainder `x - n*y` with `n` rounded to nearest-even, including scaling for small divisors, iterative reduction, sign restoration, and reserved-operand handling.

## Dependencies And Risks

- Uses VAX reserved operands rather than IEEE NaN/Inf semantics.
- `scalb` and `drem` depend on `infnan`.
- `drem` is register-heavy and relies on precise exponent scaling to avoid loss of significance.
