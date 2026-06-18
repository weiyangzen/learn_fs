<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-atomic.c -->
# sources/test-tools/stress-ng/stress-atomic.c

Purpose: `stress-atomic.c` implements the `atomic` stressor for GCC/clang `__atomic` builtins over shared stress-ng atomic fields. It stresses atomic load/store, arithmetic, bitwise, clear, fetch, and memory-order variants over 8-, 16-, 32-, and optionally 64-bit integer types.

Important APIs/types/functions: many `SHIM_ATOMIC_*` macros wrap individual `__atomic_*` builtins when available and degrade to no-op otherwise. `DO_ATOMIC_OPS()` performs 64 counted operations per call across relaxed and acquire memory orders and validates a local store/add/sub/load sequence. `stress_atomic_uint8/16/32/64()` apply the macro to `g_shared->atomic` arrays with rotating static indexes. `atomic_func_info_t` records function, metric name, and required architecture width. `stress_atomic_exercise()` runs 1000 rounds per eligible type.

Control flow: `stress_atomic()` mmaps a shared `stress_atomic_info_t` array for three children plus the parent, initializes per-process metrics and sync PIDs, forks three child workers, releases all workers at the barrier, and runs the same exercise in the parent. It then collects child statuses, kills any still running children, aggregates durations/counts per type, and emits per-type atomic-op rates.

State and persistence behavior: no files are persisted. Shared state is the mmap metrics array plus the global `g_shared->atomic` storage being mutated concurrently. Per-function static indexes select different array slots and are process-local after fork. Metrics are aggregated after child reaping.

Dependencies and integration points: it uses stress-ng shared memory (`g_shared`), fork synchronization, kill helpers, process states, metric helpers, and compile-time feature checks for `__atomic` builtins. 128-bit support is explicitly disabled with `#undef HAVE_INT128_T`. GCC 11 NAND builtins are worked around with and/xor sequences to avoid a known lock-up.

Risks: macro fallback to `DO_NOTHING()` means partial compiler feature sets can produce weaker-than-expected coverage while still compiling if at least one atomic operation exists. The validation check only proves local unshared load/store behavior, not correctness of all concurrent operations. Static indexes assume the shared arrays have power-of-two sizes because they use mask wrapping.

Test signals: build matrix coverage across compilers and 32-/64-bit targets is important, especially GCC 11 NAND behavior and missing builtin configurations. Runtime signals include child exit failures, validation failures named by integer type, and metrics such as `uint64 atomic ops per sec`, `uint32 atomic ops per sec`, etc.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-atomic.c -->
