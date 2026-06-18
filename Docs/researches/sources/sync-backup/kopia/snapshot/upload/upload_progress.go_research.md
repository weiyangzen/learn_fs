# sources/sync-backup/kopia/snapshot/upload/upload_progress.go

## Purpose
Defines upload progress callbacks and a counter-based implementation used by CLI/UI code.

## Important APIs, Types, and Functions
Constants define estimation modes: `classic`, `rough`, `adaptive`, and `AdaptiveEstimationThreshold`. `EstimationParameters` configures estimator choice. `Progress` is the uploader callback interface. `NullUploadProgress` is a no-op default. `Counters` captures current totals. `CountingUploadProgress` embeds `NullUploadProgress` and atomically tracks bytes/files/errors/exclusions plus mutex-protected current directory and last error. `Snapshot` and `UITaskCounters` expose state.

## Control Flow
Uploader calls `UploadStarted` and `UploadFinished` around each upload, emits hashing/cached/excluded/error/directory events during traversal, and emits estimated size from the estimator. The counting implementation resets on start, increments atomic counters in event methods, stores errors under lock, and builds UI counters with estimated values omitted in final mode.

## State and Persistence Behavior
No persistent state. Counters are in-memory and concurrency-safe for uploader parallelism. `UploadStarted` resets the struct, so callers should snapshot before starting a new upload.

## Dependencies and Integration Points
Used by `Uploader.Progress`, estimator settings, and `internal/uitask`. Tests access counters directly because they are in the same package.

## Risks
`Snapshot` omits `TotalExcludedFiles`, `TotalExcludedDirs`, and `TotalUploadedBytes`, while `UITaskCounters` includes them; consumers must choose the right API. `FinishedHashingFile` increments hashed file count even for failed hash attempts because uploader defers it after starting hash progress. `UploadedBytes` is only useful if lower layers call it; file copy reports `HashedBytes`.

## Test Signals
`upload_test.go` checks ignored progress is not double-counted, `FinishedFile` is invoked for success/error/cache paths, and log/UI-adjacent counters match upload outcomes.
