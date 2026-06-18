# sources/storage-engines/foundationdb/bindings/c/test/mako/utils.cpp

## Purpose
`utils.cpp` provides the non-template implementations for Mako utility helpers declared in `utils.hpp`.

## Important APIs, Types, and Functions
- `computeThreadPortion` divides a total value across process/thread partitions, distributing remainders to lower global worker indexes and returning `-1` when the base interval is zero and the current worker receives no portion.
- `digits` returns the decimal digit count for a positive integer-like input.

## Control Flow
`computeThreadPortion` is used through `computeThreadTps` and `computeThreadIters`. Validation in `mako.cpp` tries to ensure per-thread portions are positive for configured throttling/iteration runs. `digits` is used during argument initialization and key formatting.

## State and Persistence Behavior
The file has no mutable global state and no persistence. It performs deterministic arithmetic based on inputs.

## Dependencies and Integration Points
It includes `utils.hpp`, `mako.hpp`, C library headers, and fmt. Its results feed row partitioning, TPS throttling, and iteration limits in the main workload driver.

## Risks
`digits(0)` returns 0, which is acceptable for current callers because `rows` is validated positive, but it is not a general decimal-width helper for zero. `computeThreadPortion` uses integer division and returns `-1` as a sentinel that callers must handle.

## Test Signals
Unit tests should cover exact division, remainder distribution, too-small totals, and digit counts for boundary row values.
