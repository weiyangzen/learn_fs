<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp.c -->
# sources/test-tools/stress-ng/stress-fp.c Research

Purpose: implements `fp`, a CPU/FP/compute stressor that performs reversible floating-point add, subtract, multiply, and divide loops across native and optional extended FP types.

Important APIs/types/functions: `fp_data_t` stores initialization values, result slots, addends, and multipliers for long double, double, float, and optional `__bf16`, `_Float16`, `_Float32`, `_Float64`, `__float80`, `__float128`/`_Float128`, and `__ibm128`. Macros `STRESS_FP_ADD/SUB/MUL/DIV` generate optimized target-cloned worker functions. `stress_fp_funcs[]` maps method names to functions and FP type IDs. `stress_fp_call_method()` dispatches a method, updates metrics, and optionally verifies by running a second result slot and comparing byte-identical results for supported types.

Control flow: `stress_fp()` catches SIGILL, allocates a small anonymous `fp_data` array, initializes all compiled FP fields with random but reversible operands, synchronizes, and repeatedly calls either a selected `fp-method` or `all`. On exit it emits Mfp-ops/sec metrics for each method with recorded counts and durations, then unmaps the data.

State and persistence: all FP data lives in a private anonymous mapping named `fp-data`. Metrics are static per-process arrays reset per invocation. No durable files are used.

Dependencies and integration: depends on architecture/compiler feature macros, stress-ng mmap/madvise/signal/metrics/random helpers, target clone attributes, and the settings method selector. It exports `stress_fp_info` with optional verification and `max_metrics_items`.

Risks: extended FP availability is compiler- and architecture-dependent; the source disables float80 under ICC and float128 on OpenBSD. Byte-for-byte verification may be sensitive to precision, padding, or interruption; the code avoids checking after a stop signal. Division loops check the global continue flag because they can be longer-running.

Test signals: expected signals are bogo progress, per-method Mfp-ops/sec metrics, SIGILL-safe behavior on unsupported instructions, and optional verification failures that identify method, FP type, element, and expected/got values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp.c -->
