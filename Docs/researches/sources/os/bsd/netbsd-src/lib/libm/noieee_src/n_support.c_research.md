# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_support.c

Provides old no-IEEE support routines for elementary functions: `scalb`, `copysign`, `logb`, `finite`, `drem`, and `sqrt`.

Key behavior:
- Manipulates floating-point sign/exponent words directly, with separate VAX/Tahoe, IEEE, and `national` word-order paths.
- `scalb` scales by powers of two and handles subnormal normalization, overflow, and underflow.
- `copysign` transfers the sign bit.
- `logb` returns unbiased exponent and special values for zero, infinity, and NaN.
- `finite` tests exponent fields.
- `drem` implements IEEE remainder by recursive scaling and subtractive reduction.
- `sqrt` implements a bit-by-bit square-root algorithm with final rounding decisions.
- Contains disabled alternative `drem` and `sqrt` implementations that require machine-dependent floating-point status hooks.

Notable risks:
- The active code depends on strict object representation assumptions and pointer casts to integer word types.
- Comments warn these routines are slow and intended as temporary C fallbacks where machine-specific assembly is unavailable.
