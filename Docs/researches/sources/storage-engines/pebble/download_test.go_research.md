# sources/storage-engines/pebble/download_test.go

## Purpose
Provides focused datadriven tests for the internal download task scanner and bookmark state machine without running full DB compactions.

## Important APIs, Types, And Functions
`TestDownloadTask` drives `newDownloadSpanTask` and `tryLaunchDownloadCompaction` with parsed manifest versions. `initDownloadTestProvider` builds an object provider with local table backings 1-99 and external backings 100-199. The test hook `downloadSpanTask.testing.launchDownloadCompaction` simulates successful or cancelled downloads.

## Control Flow
The datadriven commands define an LSM, mark tables compacting or not compacting, create a task over a span, and repeatedly attempt launches with a configurable concurrency limit. Simulated successful downloads mutate metadata from virtual/external to local by flipping `Virtual` and `DiskFileNum`; simulated failures return `ErrCancelledCompaction` to force bookmark rescans.

## State And Persistence Behavior
The test does not persist a real Pebble DB. It mutates in-memory `manifest.Version` metadata and object-provider catalogs to model local versus external backings. It prints bookmark cursors, end bounds, task cursor state, launched table numbers, and completion state.

## Dependencies And Integration Points
Depends on `datadriven`, `manifest.ParseVersionDebug`, `manifest.L0Organizer`, `objstorageprovider`, in-memory local and remote object storage, and `testdata/download_task`. It validates the implementation in `download.go` at the manifest/task layer.

## Risks And Edge Cases
The tests focus on files overlapping the left edge of a span, compacting files that cannot launch immediately, cancelled downloads, cursor advancement, and max-concurrent bookmark limiting. They do not validate real compaction output, event listener behavior, or end-to-end external ingestion.

## Test Signals
The output is the signal: deterministic printed cursors/bookmarks show whether the scanner advances, stalls, retries, or completes at the expected point.
