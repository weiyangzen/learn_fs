# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lgamma.c

Implements legacy `lgamma()`, `lgamma_r()`, and long-double aliases where applicable. It computes log-gamma with sign reporting through `signgam` or an explicit pointer.

Key behavior:
- `lgamma()` calls `lgamma_r(x, &signgam)`.
- For large positive `x`, `large_lgam()` applies a Stirling-style expansion using split log results from `__log__D()`.
- For positive `x < 6`, `small_lgam()` reduces via gamma recurrence and chooses between two rational approximations.
- For tiny nonzero `x`, returns `-log(|x|)` and sets negative sign for negative values.
- For negative values, `neg_lgam()` uses either `gamma(x)` for not-too-negative inputs or a reflection formula for large negative values.
- Nonpositive integers return infinity; nonfinite inputs return NaN/Inf per target mode.

Important dependencies: `mathimpl.h`, `gamma()`, `__log__D()`, `log()`, `log1p()`, `sin()`, `cos()`, `floor()`, `ceil()`, and `M_PI`.

Notable risks:
- Shares old global `signgam` state.
- Uses target-specific `TRUNC()` word manipulation and endian detection for precision splitting.
