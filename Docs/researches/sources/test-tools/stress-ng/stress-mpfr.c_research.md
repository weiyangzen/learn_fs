# sources/test-tools/stress-ng/stress-mpfr.c

Purpose: implements `mpfr`, a CPU/floating-point stressor for GMP/MPFR multi-precision arithmetic. It computes several constants and functions at configurable precision and verifies deterministic repeatability.

Important APIs/types/functions: `stress_mpfr_method_t` maps method names to functions. Implemented computations include Apéry's constant, cosine and sine sums, Euler's number, exponent/log sums, binary-search square root, Omega constant, and golden ratio. `stress_mpfr()` configures precision, runs each method twice from the same MWC seed, compares `mpfr_t` results, and reports per-method rates.

Control flow: after choosing `mpfr-precision` with minimize/maximize support, the stressor initializes two result variables, synchronizes, then loops through all methods while running. For each method it snapshots RNG seeds, computes into `r0`, restores seeds, computes into `r1`, increments bogo operations for each computation, and fails if `mpfr_cmp()` differs. Deinit clears MPFR variables/caches and emits metrics.

State and persistence: MPFR temporaries are local to each method and cleared before return; `mpfr_free_cache()` is called frequently and at deinit. Static metrics are reset per run. No external state is created.

Dependencies and integration: requires `gmp.h`, `mpfr.h`, and libmpfr. Uses stress-ng settings, RNG seed controls, timing, metrics, synchronization, and verification.

Risks and test signals: high precision can be CPU and memory intensive. The deterministic comparison relies on resetting stress-ng RNG seeds around methods that use randomness. Useful signals are no inconsistency failures, nonzero per-method computation rates, correct unimplemented path without MPFR/GMP, and cache cleanup.
