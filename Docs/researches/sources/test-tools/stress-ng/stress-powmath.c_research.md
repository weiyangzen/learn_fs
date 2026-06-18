# sources/test-tools/stress-ng/stress-powmath.c

Purpose: `stress-powmath.c` implements the `powmath` stressor, repeatedly calling scalar and complex power/root/hypotenuse math functions and verifying deterministic sums against first-run baselines.

Important APIs/types/functions: `stress_powmath_method_t` maps method names to function pointers. Methods include complex `cpow*`/`csqrt*`, scalar `cbrt*`, `hypot*`, `pow*`, and `sqrt*` variants when available. Each method loops `STRESS_POWMATH_LOOPS` times, accumulates a sum, sets a static expected result on first run, and returns true on mismatch beyond `PRECISION` or `PRECISION_L`. `stress_powmath_exercise()` records per-method duration/count metrics.

Control flow: `stress_powmath()` reads `powmath-method`, zeroes metrics, synchronizes, and repeatedly exercises the selected method. The `all` method calls every concrete method in table order. On mismatch, the stressor reports failure and exits the loop. At deinit it emits per-method operation-rate metrics for every method exercised.

State and persistence behavior: state is static per-method first-run result/flag pairs and a static metrics array. No heap, files, or child processes are used. Static baselines persist for the process lifetime.

Dependencies and integration points: libm functions through shim wrappers, optional `complex.h`, target clone optimization, stress-ng method option parsing, bogo counters, and `CLASS_CPU | CLASS_FP | CLASS_COMPUTE` registration with `VERIFY_ALWAYS`.

Risks: first-run baselines make repeatability local to one process and toolchain/libm configuration; floating-point mode changes or CPU-specific math differences can trip verification. Some methods are compiled conditionally, so method indexes depend on available headers/functions. The `all` method reports specific mismatches only for concrete method indexes.

Test signals: `--powmath` and each `--powmath-method` should produce per-function ops/sec metrics and no mismatch. Coverage should include builds with no complex support, long double variants, target-clone-enabled builds, and different CPU/libm combinations.
