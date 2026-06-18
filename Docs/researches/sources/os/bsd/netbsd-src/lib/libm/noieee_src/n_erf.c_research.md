# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_erf.c

Implements legacy double `erf()`, `erfc()`, and float wrappers. The file uses multiple polynomial/rational approximations selected by `|x|`, with McIlroy modifications for accuracy.

Key behavior:
- Handles infinities and NaNs explicitly.
- For `|x| < 0.84375`, uses `x + x*P(x^2)` for `erf()` and stable `1-erf(x)` forms for `erfc()`.
- For `0.84375 <= |x| < 1.25`, uses rational approximation around a single-precision constant `c`.
- For larger values, evaluates asymptotic `erfc` forms over `[1.25,2]`, `[2,4]`, and `[4,28]`.
- Uses `__exp__D()` with split exponent terms to reduce cancellation and overflow risk.
- `erff()` and `erfcf()` cast the double results.

Important dependencies: `mathimpl.h`, `finite()`, `isnan()`, `exp()`, `__exp__D()`, and target-specific `TRUNC`.

Notable risks:
- Uses type-punning `TRUNC()` on IEEE targets.
- Many constants include folded tail terms such as `lsqrtPI_lo`, so coefficient changes are tightly coupled.
