# sources/storage-engines/foundationdb/bindings/c/test/mako/stats.hpp

## Purpose
`stats.hpp` implements Mako's metrics containers: operation counts, conflicts, errors, timeouts, latency DDSketches, JSON serialization, and CPU utilization timers for worker threads, worker processes, and FDB network threads.

## Important APIs, Types, and Functions
- `DDSketchMako` serializes/deserializes `DDSketch<uint64_t>` fields to RapidJSON.
- `WorkflowStatistics` stores per-operation counters, latency sample counts/totals, and sketches. It supports `combine`, increment methods, `addLatency`, warmup `subtractCounters`, file serialization, and sketch replacement.
- `operator<<` and `operator>>` serialize/deserialize full workflow stats.
- `CPUUtilizationTimer`, `ThreadStatistics`, and `ProcessStatistics` measure wall duration and CPU time using `flow/Platform.h` helpers.

## Control Flow
Workers mutate their own `WorkflowStatistics` slots as operations complete. Periodic stats aggregate all worker slots. At final report time, Mako loads per-thread sketch files, merges sketches, updates the aggregate stats with merged latency distributions, and prints percentile/mean/min/max metrics.

## State and Persistence Behavior
`WorkflowStatistics` is mutable in memory and also persists to JSON for exported sketch reports or temp per-op sample files. The warmup subtraction only subtracts counters, not latency sketches, so report text explicitly notes latency still includes warmup.

## Dependencies and Integration Points
It depends on `mako.hpp` for `MAX_OP`, `operations.hpp` for names and abstract op detection, `time.hpp`, `ddsketch.hpp`, RapidJSON, and platform CPU-time helpers. Shared memory embeds these classes in `shm.hpp`.

## Risks
Serialization assumes all expected JSON members exist. `operator>>` deserializes a sketch for every op name, which can fail if exported files omit empty op sketches. `combine` increments `total_errors` and `total_timeouts` by per-op errors while also combining other fields; this is fine for fresh aggregates but repeated combine into a non-fresh target must be intentional. Vectors inside shared-memory objects are process-private allocations after fork and should not be treated as portable shared-memory containers.

## Test Signals
Tests should cover DDSketch serialize/deserialize round trips, combining multiple workers, warmup counter subtraction, percentile reporting after temp-file merge, and report mode merging multiple exported sketch files.
