<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chyperbolic.c -->
# sources/test-tools/stress-ng/stress-chyperbolic.c

## Purpose
Implements the `chyperbolic` compute stressor, repeatedly evaluating complex hyperbolic functions and verifying accumulated checksums for double, float, and long double variants.

## Important APIs, Types, and Functions
`stress_chyperbolic_info` registers the stressor, `chyperbolic-method`, and up to nine metrics. `stress_chyperbolic_method_t` maps names to function callbacks. Generated methods cover available `ccosh`, `ccoshf`, `ccoshl`, `csinh`, `csinhf`, `csinhl`, `ctanh`, `ctanhf`, and `ctanhl`. `stress_chyperbolic_exercise()` times each selected function and reports checksum failures.

## Control Flow
The stressor reads the selected method index, zeros method metrics, synchronizes, and repeatedly invokes either the selected method or `all`. Each function loops `STRESS_CHYPERBOLIC_LOOPS` times over a deterministic complex progression, accumulates a sum, increments bogo operations, and returns whether the sum exceeds its precision tolerance. On exit, per-method operation rates are emitted.

## State and Persistence Behavior
State is purely in-process: static metrics, deterministic loop constants, and current method selection. No files, shared memory, or kernel state are modified.

## Dependencies and Integration Points
Depends on `<complex.h>`, math functions and shim wrappers, stress-ng target-clone optimization macros, metrics, settings, sync, and method option parsing. If complex support is absent, it registers an unimplemented stressor.

## Risks and Edge Cases
Floating-point results vary with library, architecture, precision, and optimization, so tolerances differ by type. Long double precision is adjusted based on storage size. Compiler or libm bugs surface as checksum failures. The `all` method aggregates failures but only emits named failure details for nonzero indexes.

## Test Signals
Good signals are no checksum failure logs, nonzero per-method ops/sec metrics for compiled methods, and successful method selection for `all` and each individual complex hyperbolic function available on the platform.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chyperbolic.c -->
