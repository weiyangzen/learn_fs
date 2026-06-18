<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitops.c -->
# sources/test-tools/stress-ng/stress-bitops.c

Purpose: `stress-bitops.c` implements the `bitops` CPU/integer/compute stressor. It benchmarks and self-verifies common bit manipulation idioms against simpler baseline implementations.

Important APIs/types/functions: `stress_bitops_method_info_t` maps method names to functions. Methods include `abs`, `bswap`, `countbits`, `clz`, `ctz`, `cmp`, `log2`, `max`, `min`, `parity`, `pwr2`, `reverse`, `rnddnpwr2`, `rnduppwr2`, `sign`, `swap`, and `zerobyte`, plus rotating `all`. Conditional builtins include popcount, clz, ctz, parity, and bitreverse. `stress_bitops_callfunc()` measures a method and accumulates per-method metrics.

Control flow: `stress_bitops()` clears metrics, selects `bitops-method`, waits at the sync barrier, then repeatedly calls the selected method until failure or stop, incrementing bogo operations after each successful call. The `all` method delegates through `stress_bitops_callfunc()` to one concrete method per invocation, rotating through all non-`all` entries. At deinit, metrics are reported for methods that accumulated measured duration.

State and persistence behavior: no files or kernel objects are persisted. Runtime state is local arithmetic state, the static rotation index in `stress_bitops_all()`, and the global metrics array. `stress_put_uint32()` consumes sums to keep optimizing compilers from removing work.

Dependencies and integration points: the stressor uses stress-ng random number generation, target-clone annotations, architecture and builtin feature macros, option method selection, sync barriers, process states, and metrics. It registers `VERIFY_ALWAYS` and exposes `max_metrics_items`.

Risks: several methods rely on signed shifts, overflow-style wraparound, or compiler builtin semantics; cross-compiler and sanitizer builds may behave differently even when the stressor is valid for stress-ng's supported build modes. The top-level direct call path ignores the `count` returned by the selected method except for `all`, so metrics are primarily populated when `all` is selected.

Test signals: run every individual `bitops-method` plus `all`, across compilers with different builtin availability. Failures identify the method and mismatched values. Metrics are named `<method> mega-ops per second` for measured delegated calls.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitops.c -->
