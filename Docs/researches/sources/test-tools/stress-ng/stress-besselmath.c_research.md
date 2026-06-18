<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-besselmath.c -->
# sources/test-tools/stress-ng/stress-besselmath.c

Purpose: `stress-besselmath.c` implements the `besselmath` CPU/floating-point stressor. It repeatedly calls available libc Bessel functions (`j*` and `y*` families for double, float, and long double) and verifies deterministic sums.

Important APIs/types/functions: `stress_besselmath_method_t` maps method names to functions. Each generated function such as `stress_besselmath_j0()`, `stress_besselmath_jnf()`, or `stress_besselmath_y0l()` runs `STRESS_BESSELMATH_LOOPS` iterations over incrementing inputs, accumulates a sum, stores the first-run result in a static variable, increments bogo operations, and returns true if later sums differ beyond `PRECISION` or `PRECISION_L`. `stress_besselmath_all()` dispatches all available methods through `stress_besselmath_exercise()`.

Control flow: `stress_besselmath()` selects `besselmath-method` defaulting to `all`, clears the method metrics, waits at the sync barrier, and loops until stopped or a selected method reports a mismatch. At deinit it emits per-method operation rates for methods that ran.

State and persistence behavior: there is no persistent file or kernel state. Static per-method first-run/result variables act as process-local reference baselines. `stress_besselmath_metrics[]` stores duration and call count for later metric reporting.

Dependencies and integration points: the stressor depends on `<math.h>`, stress-ng math shim functions (`shim_j0`, `shim_y0f`, etc.), compile-time `HAVE_*` checks per libc function, option method selection, process-state tracking, sync barriers, and metrics. If no supported Bessel functions are available it registers an unimplemented method selector and `stress_unimplemented`.

Risks: static reference sums assume deterministic libc behavior for the same process and floating-point environment; changes to rounding modes, libm vectorization, or architecture-specific precision can cause false positives. `all` does not report a method name in the first failure except through the nested nonzero index check.

Test signals: build coverage should include systems with only double functions, with float/long-double variants, and with none. Runtime tests should use individual methods and `all`, verify mismatch reporting, and check metrics like `j0 ops per second`, `ynf ops per second`, and long-double variants when present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-besselmath.c -->
