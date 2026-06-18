# sources/storage-engines/foundationdb/bindings/c/test/mako/shm.hpp

## Purpose
`shm.hpp` defines Mako's shared-memory protocol between the parent, worker processes, worker threads, async workflows, and stats process. It provides a safer accessor around a manually packed POSIX shared-memory buffer.

## Important APIs, Types, and Functions
- `SIGNAL_RED`, `SIGNAL_GREEN`, and `SIGNAL_OFF` coordinate lifecycle.
- `shared_memory::Header` stores atomic signal, ready count, throttle factor, and stop count.
- `storageSize` computes required bytes for header, worker `WorkflowStatistics`, `ThreadStatistics`, and `ProcessStatistics`.
- `shared_memory::Access` wraps base pointer and dimensions, placement-news statistics objects, and exposes array/slot accessors.

## Control Flow
`mako.cpp` creates and maps shared memory, constructs `Access`, calls `initMemory`, then passes the accessor by value into children and threads. Workers increment readiness, check signal state, update stats slots, and increment stop count. The stats process reads arrays and throttle signal; the parent writes lifecycle signals.

## State and Persistence Behavior
All state is transient shared memory. Objects are placement-constructed in a contiguous layout and are never explicitly destroyed before unmapping, which is acceptable for process-local benchmark termination but important because contained vectors in `WorkflowStatistics` are copied into shared memory.

## Dependencies and Integration Points
It depends on `stats.hpp` and atomics. Layout alignment relies on `alignas(64)` in stats classes and on all processes using the same binary ABI. `storageSize` must match `Access` pointer arithmetic exactly.

## Risks
Manual layout arithmetic is fragile. `storageSize` asserts only minimal positive dimensions and does not validate overflow. Objects containing non-trivial members in shared memory are safe after fork in this single-binary model but would not be a general cross-process ABI. Async mode passes `num_workers = async_xacts` while thread timer storage still uses `num_threads`, so callers must supply consistent dimensions.

## Test Signals
Stress runs with multiple processes, multiple threads, and async workflows are the practical tests. Sanitizer or debug builds should verify no slot overruns. Unit tests for `storageSize` and slot address monotonicity would reduce risk.
