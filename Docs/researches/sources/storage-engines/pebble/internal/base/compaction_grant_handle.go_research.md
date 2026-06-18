<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/compaction_grant_handle.go -->
# sources/storage-engines/pebble/internal/base/compaction_grant_handle.go

## Purpose
This file defines interfaces and small types used by compactions to report resource usage to a scheduler.

## Important APIs, Types, And Functions
`CompactionGrantHandleStats` currently carries cumulative write bytes. `CompactionGrantHandle` requires `Started`, `MeasureCPU`, `CumulativeStats`, and `Done`. `CompactionGoroutineKind` identifies primary SST/blob worker goroutines. `CPUMeasurer` abstracts CPU measurement, and `NoopCPUMeasurer` is a no-op implementation.

## Control Flow
There is no implementation flow besides `NoopCPUMeasurer.MeasureCPU` doing nothing. Comments define lifecycle ordering: `Started` first, frequent measurement/stat calls, and `Done` after version install without locks.

## State And Persistence Behavior
The file stores no state and persists nothing. It defines contracts for runtime scheduling.

## Dependencies And Integration Points
Compaction code and schedulers use these contracts to pace disk/CPU work and schedule follow-up compactions.

## Risks And Edge Cases
Callers must avoid holding locks across `Done` because it may synchronously schedule more work. Missing `MeasureCPU` calls can undercount resource use.

## Test Signals
No direct tests in this subset; expected coverage is through compaction scheduler tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/compaction_grant_handle.go -->
