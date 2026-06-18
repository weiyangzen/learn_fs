# sources/storage-engines/pebble/internal/inflight/in_flight.go

## Purpose
`in_flight.go` implements a low-overhead tracker for long-running operations. Callers start and stop handles around work, and reports identify operations older than a threshold grouped by caller stack.

## Important APIs, Types, And Functions
`Tracker` owns sharded `xsync.MapOf[Handle, entry]` maps, padded handle counters, and optional polling timer state. `Handle` is an opaque nonzero token. Public APIs include `NewTracker`, `NewPollingTracker`, `Close`, `Start`, `Stop`, and `Report`. `olderThan` yields entries before a cutoff. Internal `entry` stores monotonic start time and a seven-frame `stack`.

## Control Flow
`Start` captures monotonic time and caller PCs, selects a CPU-biased shard, generates a handle with shard index in the high byte, and stores the entry. `Stop` deletes from the shard encoded in the handle. `Report` scans all shards for old entries, groups by stack, keeps occurrence count and oldest start, sorts groups by age, and formats resolved frames. `NewPollingTracker` schedules a timer that periodically reports non-empty summaries and resets itself until `Close`.

## State And Persistence Behavior
All state is in-memory and concurrency-safe. Handles are unique per shard counter until wraparound. Reports are ephemeral strings; polling invokes a caller-supplied function but does not persist.

## Dependencies And Integration Points
It depends on `crsync` shard helpers, `crtime.Mono`, `xsync`, `runtime`, Go 1.23 `iter`, maps/slices helpers, atomics, and timers. It is intended for subsystems that need lightweight stuck-operation diagnostics.

## Risks And Edge Cases
Stopping a zero handle indexes shard 0 after shifting and is not guarded; callers should use valid handles. `runtime.Callers` depth and inlining affect grouping. `Close` stops future polling but `Start`, `Stop`, and `Report` remain usable.

## Test Signals
`in_flight_test.go` checks basic report thresholding and polling timer behavior under synctest. `in_flight_bench_test.go` measures Start/Stop overhead across parallelism.
