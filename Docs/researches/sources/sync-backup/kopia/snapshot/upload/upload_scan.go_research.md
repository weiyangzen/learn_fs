# sources/sync-backup/kopia/snapshot/upload/upload_scan.go

## Purpose
Adapts the upload estimator's scan progress callback into simple final file-count and byte totals.

## Important APIs, Types, and Functions
`scanResults` stores `numFiles` and `totalFileSize`. It implements `EstimateProgress` with no-op `Error` and `Processing`, and a `Stats` method that copies final `snapshot.Stats.TotalFileCount` and `TotalFileSize` using atomic loads.

## Control Flow
Classic estimation calls `Estimate` with `scanResults`. Intermediate stats are ignored; only `final == true` updates the totals used by `doClassicEstimation`.

## State and Persistence Behavior
In-memory only. It intentionally ignores scan errors in the progress callback; `Estimate` returns the actual terminal error.

## Dependencies and Integration Points
Depends on `snapshot.Stats` and the scanner's `EstimateProgress` contract. Used by `upload_estimator.go`.

## Risks
Only final stats are captured, so if `Estimate` changes to omit a final call on partial success the estimator returns zeroes. `numFiles` narrows from `int32` through `int`; this is acceptable on supported platforms but is a theoretical portability concern.

## Test Signals
Covered indirectly by classic estimator tests and ignore-policy estimator tests.
