# sources/storage-engines/foundationdb/bindings/c/test/mako/utils.hpp

## Purpose
`utils.hpp` contains inline and template helpers for random data, key generation, row partitioning, RAII guards, and fixed-width terminal output used throughout Mako.

## Important APIs, Types, and Functions
- Random helpers: `urand`, `nextKey`, `randomAlphanumString`, and `randomString`.
- Key helpers: `insertBegin`, `insertEnd`, `numericWithFill`, `genKey`, and `prepareKeys`.
- Partition helpers: declarations for `computeThreadPortion`, `computeThreadTps`, and `computeThreadIters`.
- RAII helpers: `ExitGuard` and `FailGuard`.
- Formatting helpers: `putTitle`, `putTitleRight`, `putTitleBar`, `putField`, `putFieldBar`, and `putFieldFloat`.

## Control Flow
Workload execution calls `prepareKeys` once per operation's first step, generating row keys using either uniform or Zipfian distribution. Build mode uses `insertBegin`/`insertEnd` to assign disjoint row ranges. Cleanup and stats printing use the formatting helpers. Guards are used in `mako.cpp` to reset stopwatches, reset transactions, join/stop network threads, and clean resources at scope exit.

## State and Persistence Behavior
Most helpers are stateless. Random helpers consume the process-global C `rand()` state seeded in `main`; Zipf selection consumes the FDB zipfian generator state. Key generation only mutates caller-provided buffers.

## Dependencies and Integration Points
It depends on `mako.hpp`, `macro.hpp`, `fdbclient/zipf.h`, fmt, and C/C++ standard headers. It is a low-level dependency of operations and the Mako driver.

## Risks
`rand()` is process-global and not high-quality; worker threads call these helpers concurrently, so randomness may be implementation-dependent. Key buffer lengths rely on prior validation. `ExitGuard` always executes and is non-copy-protected, so accidental copies would double-run callbacks. Formatting helpers print directly to stdout.

## Test Signals
Tests should verify key layout with and without prefix padding, range endpoint generation, Zipf/uniform selection bounds, and partition coverage with no gaps or overlaps across process/thread combinations.
