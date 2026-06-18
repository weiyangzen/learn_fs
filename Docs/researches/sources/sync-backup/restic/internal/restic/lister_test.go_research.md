<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister_test.go -->
# sources/sync-backup/restic/internal/restic/lister_test.go

## Purpose
Tests the memoized lister wrapper from the external `restic_test` package to exercise the exported API.

## Important APIs and Control Flow
`ListHelper` implements `restic.Lister`; `TestMemoizeList` builds a fake list source, memoizes snapshot files, verifies mismatched file types fail, and replays the cached IDs/sizes. `TestMemoizeListError` confirms source-list errors abort memoization. Each test uses callbacks to model backend iteration and `internal/test` assertions for equality and error handling.

## State, Persistence, Dependencies, and Integration
State is test-local generated IDs and slices. Dependencies include `backend.FileType`, exported restic APIs, and the shared test helpers.

## Risks and Test Signals
The tests signal correct cache replay and error propagation but do not cover context cancellation or concurrent use of the memoized lister.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister_test.go -->
