# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_jn.c

This file implements double-precision order-`n` Bessel functions `__ieee754_jn(int n, double x)` and `__ieee754_yn(int n, double x)`.

`jn` normalizes negative orders using Bessel parity rules, delegates orders 0 and 1 to `j0`/`j1`, uses forward recurrence when `n <= x`, uses a large-`x` asymptotic shortcut above `2**302`, and otherwise computes a continued-fraction estimate followed by backward recurrence and normalization against `j0` or `j1`. Tiny `x` uses the leading Taylor term `(x/2)^n/n!`.

`yn` rejects zero and negative arguments, normalizes negative orders by sign parity, delegates orders 0 and 1, returns zero for infinite positive input, uses a large-`x` asymptotic formula, and otherwise uses forward recurrence from `y0`/`y1`, stopping if `-inf` is reached.

Dependencies include the order-0/order-1 Bessel kernels, `sin`, `cos`, `sqrt`, `fabs`, `__ieee754_log`, and IEEE word inspection macros.
