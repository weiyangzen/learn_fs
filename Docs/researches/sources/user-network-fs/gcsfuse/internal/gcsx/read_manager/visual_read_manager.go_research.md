# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager.go

## Scope

This file implements `VisualReadManager`, a `gcsx.ReadManager` wrapper that records requested read ranges and renders a workload insight visualization when destroyed.

## Purpose

The wrapper provides optional observability for file read patterns without changing the underlying read implementation. It can print the visualization to stdout or append it to a configured output file.

## Important APIs, Types, And Functions

- `VisualReadManager` stores the wrapped manager, renderer, recorded ranges, mutex, workload insight config, and forward merge threshold.
- `NewVisualReadManager` constructs the wrapper.
- `ReadAt` records a range for non-empty buffers and delegates to the wrapped manager.
- `Destroy` renders and outputs the visualization, then destroys the wrapped manager.
- `acceptRange`, `mergeRanges`, and `appendToFile` implement range collection and output.

## Control Flow

`ReadAt` records `[Offset, Offset+len(Buffer))` before the wrapped read runs. `acceptRange` clamps the end to object size, then tries to merge only with the last recorded range. `mergeRanges` merges adjacent or forward-near ranges within the configured threshold, but does not merge overlapping ranges. `Destroy` renders using object name, object size, and accumulated ranges.

## State And Persistence Behavior

Recorded ranges live in memory until `Destroy`. Output persistence is append-only to `cfg.OutputFile` with mode `0600`; if no file is configured, output goes to stdout. The wrapper does not persist read results or cache content.

## Dependencies And Integration Points

It depends on `cfg.WorkloadInsightConfig`, `workloadinsight.Renderer`, `workloadinsight.Range`, `logger`, and the `gcsx.ReadManager` interface. It is intended to wrap any concrete read manager.

## Risks And Maintenance Notes

The wrapper records attempted reads before knowing whether they succeed, so visual output may include failed reads. It only merges with the most recent range and refuses overlapping merges, which preserves request chronology but may fragment repeated/overlapping workloads. `Destroy` calls `Object()` during rendering; wrapped managers must still be valid. Output failures print to stdout and warn, so callers do not receive an error.

## Test Signals

`visual_read_manager_test.go` validates construction, range acceptance, adjacent and threshold-based merging, non-merging overlaps, read delegation, destroy delegation, output file creation, append behavior, and empty output-path errors.
