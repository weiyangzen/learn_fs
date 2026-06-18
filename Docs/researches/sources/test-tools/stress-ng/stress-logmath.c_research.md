# sources/test-tools/stress-ng/stress-logmath.c

Purpose: implements `logmath`, a CPU/floating-point stressor for logarithmic math functions. It exercises real and complex `log`, `logb`, `log10`, and `log2` variants across float, double, and long double forms where available.

Important APIs/types/functions: `stress_logmath_method_t` maps method names to function pointers. Individual `stress_logmath_*()` functions run `STRESS_LOGMATH_LOOPS` calls, accumulate a sum, and compare future runs with the first result using `PRECISION` or `PRECISION_L`. `stress_logmath_exercise()` times one method and updates metrics. `stress_logmath_all()` iterates all concrete methods.

Control flow: the selected method defaults to `all`. After sync, the stressor repeatedly calls `stress_logmath_exercise()`. Any result drift beyond tolerance logs a failure and exits with failure. At deinit, it emits per-function operations-per-second metrics for all methods that ran.

State and persistence: each method uses static `first_run` and `result` variables as deterministic baselines. Metrics are static arrays reset at the start of each run. No filesystem or kernel state is modified.

Dependencies/integration: depends on `<math.h>`, optional `<complex.h>`, stress-ng shim math wrappers, target clone optimization, pragma unrolling, method option lookup, and metrics. It compiles to `stress_unimplemented` if no supported log function exists.

Risks/test signals: libm differences, excess precision, compiler optimizations, and complex math availability can affect reproducibility. Useful signals are method option enumeration, per-method metrics, failure messages on mismatched sums, and correct unimplemented option behavior.
