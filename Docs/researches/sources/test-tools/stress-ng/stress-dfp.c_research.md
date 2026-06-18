# sources/test-tools/stress-ng/stress-dfp.c

Purpose: implements the `dfp` CPU/FP stressor for compiler-supported decimal floating point types `_Decimal32`, `_Decimal64`, and `_Decimal128`. It repeatedly performs add, subtract, multiply, and divide loops and reports per-method throughput.

Important APIs/types/functions: `dfp_data_t` stores per-element initial values, two result slots, add/reverse-add, and multiply/reverse-multiply values for each enabled decimal type. Macro generators `STRESS_DFP_ADD/SUB/MUL/DIV` create optimized method functions. `stress_dfp_funcs[]` maps method names such as `df32add` and `df128div` to function pointers and decimal type IDs. `stress_dfp_call_method()` invokes methods, updates `stress_dfp_metrics`, and optionally verifies two runs. `stress_dfp_all()` iterates all concrete methods. `stress_dfp()` allocates data, initializes operands, runs the selected method, and emits metrics.

Control flow: after SIGILL handling and mmap allocation, `stress_dfp()` reads `--dfp-method` defaulting to `all`, initializes all decimal fields from random values, synchronizes start, clears metrics, and loops while `stress_continue(args)`. Each call performs `DFP_ELEMENTS * LOOPS_PER_CALL` logical operations per metric update. At shutdown it emits `Mdfp-ops per sec` metrics for every method with duration/count.

State and persistence behavior: state is process-local anonymous mmap named `dfp-data`; metrics use a static `stress_dfp_metrics[]` array reset at start. No filesystem state is created. Verification compares duplicate result slots using `memcmp` for exact decimal representation, but skips verification if a stop signal interrupts the second run.

Dependencies and integration points: relies on compiler feature macros `HAVE_Decimal32/64/128`, stress-ng mmap/madvise/target-clones/signal/metrics helpers, and stressor registration through `stress_dfp_info` with `CLASS_CPU | CLASS_FP | CLASS_COMPUTE | CLASS_HOT`. If no decimal types exist, the stressor is registered as unimplemented while still exposing the method option.

Risks: decimal floating point support is compiler- and architecture-dependent; invalid assumptions about type availability or exact representation can break verification. Division loops check `stress_continue_flag()` because they may be slower. Metrics for the `all` pseudo-method are distributed to concrete methods, so method-index invariants matter.

Test signals: compile on toolchains with none, some, and all decimal types; run `--dfp-method all` and each concrete method with and without `--verify`; inspect per-method metrics and confirm unimplemented messaging on unsupported builds.
