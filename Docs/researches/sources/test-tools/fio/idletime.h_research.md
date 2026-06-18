# sources/test-tools/fio/idletime.h

## Purpose
Defines idle-profiler options, status codes, shared data structures, and public API declarations.

## Important APIs, Types, and Functions
Constants include `CALIBRATE_RUNS`, `CALIBRATE_SCALE`, and `MAX_CPU_STR_LEN`. Option values distinguish none, calibration-only, system, and per-CPU profiling. Status values distinguish OK, calibration stop, profiling stop, and abort. `struct idle_prof_thread` stores thread id, CPU id, state, timestamps, calibration time, loop count, idleness, data buffer, synchronization primitives, and CPU mask. `struct idle_prof_common` aggregates all threads and global stats. Declared functions parse options, initialize/start/stop/cleanup profiling, and show stats.

## Control Flow
Runtime code sets an option through `fio_idle_prof_parse_opt()`, calls init/start/stop around job execution, emits stats after completion, and finally cleans up allocations.

## State and Persistence Behavior
The header describes in-memory profiler state only. No persistence contract is exposed.

## Dependencies and Integration Points
Includes fio `os/os.h`, pthread-visible types through platform headers, and JSON/buffer output forward usage in function declarations. Used by initialization and output paths.

## Risks
The structs expose implementation details, so changes affect every includer. Fields such as `state` rely on thread-state constants defined elsewhere.

## Test Signals
Compile-time coverage across CPU-affinity and non-affinity platforms plus runtime idle-prof option tests are the useful signals.
