# sources/test-tools/stress-ng/stress-trig.c

## Purpose
Implements the `trig` stressor, a floating-point compute workload that repeatedly evaluates trigonometric functions over deterministic ranges and verifies checksums against expected sums.

## Important APIs, Types, And Functions
`stress_trig_method_t` maps method names to function pointers. Individual methods cover double, float, and long-double `cos`, `sin`, and `tan`, plus `sincos` variants when available. Each method loops `STRESS_TRIG_LOOPS` times, accumulates a sum, increments bogo ops, and returns whether the checksum exceeds precision tolerance. `stress_trig_exercise()` times one method call, updates `stress_trig_metrics`, and logs checksum failure for non-`all` methods. `stress_trig_all()` invokes every concrete method.

## Control Flow
`stress_trig()` resolves `trig-method`, zeros metrics, synchronizes, and repeatedly exercises the selected method until stop or checksum failure. The `all` method calls all configured concrete functions in sequence. On exit it emits per-method operations/sec metrics based on loop count, call count, and accumulated duration.

## State And Persistence Behavior
State is limited to static per-method metric counters and stack-local floating point accumulators. There are no files or persistent system resources.

## Dependencies And Integration Points
The file depends on math functions through stress-ng shim wrappers, target clone annotations, put/metric helpers, and method option parsing. Optional `sincos`, `sincosf`, and `sincosl` support is compile-time gated. It registers as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Checksum tolerances differ by precision and long-double representation, but libm, compiler, architecture, and optimization differences can still affect sums. Tangent uses a range near pi with a precomputed expected sum, so it is more sensitive than sine/cosine zero-sum checks. Test signals include checksum failure logs naming the method, bogo progress, method metrics, option enumeration for only compiled-in methods, and successful operation across float/double/long-double paths.
