# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinhl.c

This file implements public long-double `asinhl(long double x)` when long double is available, with fallback to double `asinh`.

For supported ld80 and ld128 formats, it selects large and tiny exponent thresholds from mantissa precision, handles Inf/NaN, returns tiny inputs unchanged, uses `logl(fabsl(x))+ln2` for large inputs, a stable logarithm for `|x| >= 2`, and `log1pl` for smaller normal inputs. It weak-aliases `asinhl` to `_asinhl`.

Dependencies include `namespace.h`, machine IEEE layout, `math_private.h`, `sqrtl`, `logl`, `log1pl`, and long-double exponent macros.
