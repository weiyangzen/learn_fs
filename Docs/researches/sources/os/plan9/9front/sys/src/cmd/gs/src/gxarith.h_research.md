# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxarith.h

Declares integer arithmetic helpers and defines portable arithmetic/test macros used by Ghostscript graphics code.

Key definitions:
- `any_abs` works for signed numeric types.
- Declares `imod`, `igcd`, `idivmod`, and `ilog2`.
- Provides bit-fit tests for signed/unsigned integral values.
- Provides floating-point constant comparisons and range-fit tests.
- Defines `small_exact_log2` for powers of two from 1 through 128 using a compact constant expression.
- Notes a quotient/remainder trick for modulus by `2^n - 1`.

Research notes:
- Several macros are written to accommodate older compilers and no-floating-point variants referenced through `gxfarith.h`.
