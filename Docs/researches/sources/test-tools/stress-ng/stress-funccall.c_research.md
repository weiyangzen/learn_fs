<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funccall.c -->
# sources/test-tools/stress-ng/stress-funccall.c Research

Purpose: implements `funccall`, a CPU stressor that exercises ABI argument passing for functions with one through nine arguments, including shallow and nested call chains across many scalar and optional FP/complex/decimal types.

Important APIs/types/functions: macros generate `stress_funccall_<type>_1..9()` and `stress_funcdeep_<type>_1..9()` functions. `stress_funccall_type()` generates a per-type exerciser that creates nine random inputs, repeatedly sums shallow and nested call results, stores values through `core-put` helpers, and verifies stable results. `stress_funccall_methods[]` maps selectable method names to generated functions. `stress_funccall_exercise()`, `stress_funccall_all()`, and `stress_funccall()` implement dispatch, metrics, and return status.

Control flow: top-level code zeroes metrics, reads `funccall-method`, synchronizes, then repeatedly exercises either the selected type or all compiled types until a check fails or stress-ng stops. At exit it emits per-type "function invocations per sec" harmonic metrics and returns failure if verification failed.

State and persistence: metrics are static per-process arrays reset at start. Generated functions update `g_put_val` through put helpers to prevent optimization from removing work. No durable state exists.

Dependencies and integration: depends on architecture/compiler feature gates, `<math.h>`, optional complex support, decimal and extended FP feature macros, `core-put`, random number helpers, sync/state/metrics, and method-option parsing. It is VERIFY_ALWAYS with `max_metrics_items`.

Risks: macro expansion is large and type availability is compiler-sensitive. Some optional types use `cmp_ignore`, so those methods measure call paths without semantic verification. s390 and SH4 disable selected hard-decimal/complex paths. Floating comparisons use relative tolerances after casting to double, which may hide precision-specific differences.

Test signals: failure logs identify the nested method whose return value changed. Metrics should appear for every compiled method except `all`. Build coverage should include compilers with and without complex, decimal, float16/32/64/80/128, and int128 support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funccall.c -->
