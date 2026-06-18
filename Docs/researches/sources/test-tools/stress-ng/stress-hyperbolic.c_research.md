# sources/test-tools/stress-ng/stress-hyperbolic.c

## Purpose
`stress-hyperbolic.c` stresses libm hyperbolic functions by repeatedly evaluating `cosh`, `sinh`, and `tanh` in double, float, and long-double variants over fixed ranges, checking expected sums, and exporting per-function operation rates.

## Important APIs, Types, And Functions
`stress_hyperbolic_method_t` maps method names to callbacks. Methods include `cosh`, `coshf`, `coshl`, `sinh`, `sinhf`, `sinhl`, `tanh`, `tanhf`, `tanhl`, and `all`. Each method loops `STRESS_HYPERBOLIC_LOOPS` times with unroll pragmas and target clones, accumulates a sum through shim math functions, increments bogo ops, and returns whether the checksum exceeded tolerance. `stress_hyperbolic_exercise()` times one method and updates `stress_hyperbolic_metrics`.

## Control Flow
`stress_hyperbolic()` reads the selected method, zeroes metrics, waits at the barrier, repeatedly exercises the chosen method until stop or checksum failure, sets deinit state, then emits one metric per concrete method that ran. The `all` method iterates all concrete methods each pass.

## State And Persistence
State is in static metrics and stack accumulators. There is no external state or persistence.

## Dependencies And Integration Points
The file depends on stress-ng math shims, `core-put`, target-clone and pragma helpers, metrics, option parsing, and global process-state/sync helpers.

## Risks
Expected sums are tolerance-based and may vary across libm implementations, extended precision modes, compiler optimizations, and target clones. Each method increments bogo count internally, so `all` increments multiple times per outer loop. Long-double precision tolerance changes by `sizeof(long double)` but still may be platform-sensitive.

## Test Signals
Signals include successful verify-mode checks for every method, sane metrics named `<method> ops per second`, correct method selection, and no false checksum failures across supported architectures/libm variants.
