<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-misc.c -->
# sources/test-tools/stress-ng/stress-fp-misc.c Research

Purpose: implements `fp_misc`, a VERIFY_ALWAYS CPU/FP/compute stressor for C floating-point comparison and classification macros across `float`, `double`, and `long double`.

Important APIs/types/functions: global test operands hold normal values, ordered variants, NaN, infinity, and zero for each precision. `stress_fp_misc_methods_t` maps a check function, metric name, and number of logical tests. The method table includes gated checks for `isgreater`, `isgreaterequal`, `isless`, `islessequal`, `islessgreater`, `isunordered`, `fpclassify`, `isfinite`, `isnormal`, `isnan`, `isinf`, and `signbit`. `stress_fp_misc_supported()` skips builds with no available macros.

Control flow: after catching SIGILL and zeroing metrics, the stressor initializes NaN/inf/zero constants, synchronizes, then repeatedly creates ordered random values for all three precisions. For every method, it runs the check 1000 times, accumulating duration and test count. A failed check jumps to `fp_fail`, where metrics are still emitted. Each check logs a detailed failure if a comparison or classification macro violates expected behavior with ordered values, NaN, infinity, or signed zero.

State and persistence: operand globals are process-local and overwritten each iteration. Metrics are stack-local and published at exit. There is no file or shared persistent state.

Dependencies and integration: depends on `<math.h>` macros, stress-ng random number generation, signal handling, sync, metrics, bogo counters, and feature gating. The stressor reports up to one metric per compiled method.

Risks: several diagnostic strings say "returned false" in branches where the code is checking an unexpected true result; this affects logs, not control flow. `stress_fp_misc()` currently returns `EXIT_SUCCESS` even after a check failure path, relying on `pr_fail()` and VERIFY_ALWAYS as the observable signal. Macro availability and behavior can vary by libc/compiler, and NaN signbit expectations may be implementation-sensitive.

Test signals: look for per-method ops/sec metrics and any `pr_fail()` messages. Regression tests should validate builds with and without each math macro family, plus platforms where `isinf` is disabled for PCC.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-misc.c -->
