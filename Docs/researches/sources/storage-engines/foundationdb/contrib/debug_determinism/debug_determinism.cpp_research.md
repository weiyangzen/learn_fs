# sources/storage-engines/foundationdb/contrib/debug_determinism/debug_determinism.cpp

## Purpose
Implements sanitizer coverage callbacks that record and compare executed control-flow guard IDs to detect nondeterministic execution order.

## Important APIs, Types, And Functions
Defines `__sanitizer_cov_trace_pc_guard_init(uint32_t* start, uint32_t* stop)` and `__sanitizer_cov_trace_pc_guard(uint32_t* guard)`, the callbacks inserted by compiler coverage instrumentation. Internal globals `out` and `in` are `FILE*` handles to `out.bin` and `in.bin`. `loop_forever()` spins on mismatch.

## Control Flow
Initialization opens `in.bin` and `out.bin`, then assigns monotonically increasing guard IDs once per guard section. On each instrumented edge, the callback writes the guard ID to `out.bin`; if `in.bin` is available, it reads the expected ID and loops forever after printing a nondeterminism message on mismatch or premature EOF.

## State And Persistence
Persists the observed trace to `out.bin` and consumes expected trace from `in.bin` in the current working directory. Static counter `N` persists across callback invocations in-process.

## Dependencies And Integration
Requires compiler support for sanitizer coverage guard callbacks. Intended to be linked into instrumented FoundationDB binaries or DSOs.

## Risks
No null check after opening `out.bin`; `fwrite` with a null file pointer would crash. Files are reopened each initialization call before the early-return guard, potentially leaking handles across DSOs or repeated init calls. The infinite loop is intentional for debugging but hazardous in automated environments. Guard assignment order may vary by link/load order across DSOs.

## Test Signals
Run an instrumented deterministic binary twice to produce and replay `out.bin` as `in.bin`; test mismatch detection, missing `in.bin`, unwritable directory, and multiple-DSO initialization.
