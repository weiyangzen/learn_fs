# sources/test-tools/stress-ng/stress-expmath.c

Purpose: implements `expmath`, a CPU floating-point stressor for exponential math functions across real and complex `double`, `float`, and `long double` variants when libc/compiler support is available.

Important APIs/types/functions: `stress_expmath_method_t` maps method names to function pointers. Method functions such as `stress_expmath_exp()`, `stress_expmath_cexp()`, `stress_expmath_exp10l()`, and `stress_expmath_exp2f()` run 10,000 operations and compare against a first-run reference. `stress_expmath_exercise()`, `stress_expmath_all()`, and `stress_expmath()` handle method dispatch, metrics, and loop control.

Control flow: compile-time feature gates populate `stress_expmath_methods[]` with `all` plus available math functions. At runtime the selected method defaults to `all`, metrics are zeroed, workers sync-start, and each loop executes the chosen method. The `all` method invokes every concrete function, while each concrete method accumulates exponentials over normalized inputs, increments bogo operations, and returns failure if its result diverges beyond fixed precision.

State and persistence behavior: no persistent state exists. Each method has static `result` and `first_run` variables used as deterministic per-process reference values. Metrics are static arrays reset at worker start and emitted as operations per second.

Dependencies and integration points: depends on `<math.h>`, optional `<complex.h>`, stress-ng shim math wrappers, target clone/optimization pragmas, process-state, metrics, and option parsing. Unsupported builds retain the option parser but register `stress_unimplemented`.

Risks: static reference comparisons assume deterministic floating-point behavior within one process. Different libm implementations, excess precision, compiler vectorization, or fast-math settings can affect tolerances. Complex and long-double availability is highly platform-dependent.

Test signals: build with varied libm feature sets, run `--expmath-method all` and individual methods, verify per-method metrics appear, and confirm a missing function set reports unimplemented rather than accepting an invalid method silently.
