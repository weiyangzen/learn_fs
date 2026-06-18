# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager_test.go

## Scope

This file tests the visual read-manager wrapper and its file append helper using `MockReadManager` and the workload insight renderer.

## Purpose

The tests ensure the wrapper records ranges, merges only the intended range patterns, delegates reads and destroy calls, and writes visualization output when configured.

## Important APIs, Types, And Functions

- `TestNewVisualReadManager` validates constructor wiring.
- `TestVisualReadManager_AcceptRange` covers range recording and last-range merging.
- `TestVisualReadManager_MergeRanges` covers overlap, adjacency, gap, and forward-threshold cases.
- `TestVisualReadManager_ReadAt` verifies recording plus delegated read.
- `TestVisualReadManager_Destroy` and output-file variants verify rendering/destroy behavior.
- `TestAppendToFile_*` validates append helper behavior.

## Control Flow

Tests create mock read managers with optional `Object`, `ReadAt`, and `Destroy` expectations, instantiate a real workload insight renderer, invoke wrapper internals or public methods, and inspect in-memory ranges or output files.

## State And Persistence Behavior

Most state is in `vrm.readIOs`. File-output tests write `test_output.txt` or `test_append_output.txt` in the current package directory and remove them after assertions.

## Dependencies And Integration Points

It depends on `cfg.WorkloadInsightConfig`, `gcsx.ReadRequest`, `gcs.MinObject`, workload insight rendering, testify `assert/mock/require`, and local `MockReadManager`.

## Risks And Maintenance Notes

Tests for internal helpers are intentionally white-box. Output-file tests use fixed relative filenames, so interrupted tests can leave artifacts. The accept-range expectations document the current non-overlap merge rule; changing that rule will require coordinated test updates.

## Test Signals

Signals include empty initial state, exact range list after non-overlapping/overlapping/adjacent/mixed inputs, threshold merge boundaries in MB, one recorded range for a delegated read, non-empty rendered output files, append preserving previous content, and error on empty output path.
