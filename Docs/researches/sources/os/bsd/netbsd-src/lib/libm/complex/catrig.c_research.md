# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrig.c

## Scope

Modern FreeBSD-derived double complex inverse trig and inverse hyperbolic trig implementation: `casinh`, `casin`, `cacos`, `cacosh`, `catanh`, and `catan`.

## APIs And Behavior

- Defines weak aliases for `casin` and `catan`.
- Implements Hull/Fairgrieve/Tang-style algorithms for `casinh`, `casin`, `cacos`, and `cacosh`, with careful handling near branch cuts and large magnitudes.
- Core helper `f(a,b,hypot)` computes `(hypot(a,b)-b)/2` stably.
- `do_hard_work` computes `Re(casinh)` and supporting values for `asin(B)` / `atan2` paths, avoiding underflow/overflow by case analysis and scaling.
- `casinh` handles NaN/Inf cases, large values through `clog_for_large_values`, zero exactness, small `z` inexact behavior, and sign restoration.
- `casin` uses the reverse identity with `casinh`.
- `cacos` computes carefully near `z = 1`, handles large inputs through `clog_for_large_values`, and chooses `acos` or `atan2` forms depending on numeric stability.
- `cacosh` derives from `cacos` and maps signs to the principal value.
- `clog_for_large_values` avoids overflow in logarithm magnitude computation.
- `catanh` uses stable `log1p`, `atan2`, reciprocal, and large-value formulas; `catan` uses the reverse identity with `catanh`.

## Dependencies And Risks

- Depends on `math_private.h` bit macros for reciprocal scaling and on C99 complex constructors.
- Special-value handling is extensive and part of the ABI contract.
- Constants are selected for IEEE double and VAX double via `DBL_MAX_EXP`.
