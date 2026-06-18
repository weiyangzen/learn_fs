<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go

## Purpose
This legacy ogletest file is the main behavioral suite for `Job`. It validates state-machine transitions, subscriber mechanics, file-info cache mutation, sequential async download, public `Download`, cancellation, invalidation, CRC behavior, and cache file creation.

## Important fixtures and APIs
`initJobTest` creates a fake GCS object, builds a cache `FileSpec`, creates an LRU cache, constructs a `Job`, and inserts the required `data.FileInfo` entry. Helpers verify invalid errors, cache-file content, file-info entries, and cache path layout. The file notes that new tests should be added to the newer testify suite.

## Control flow and state behavior
Early tests validate `init`, `subscribe`, `notifySubscribers`, and `updateStatusAndNotifySubscribers`. Offset update tests confirm that updating an existing file-info entry changes both LRU value and job status, while missing entries return `lru.ErrEntryNotExist` and size mismatch returns `lru.ErrInvalidUpdateEntrySize`. Download tests cover starting from `NotStarted`, joining an existing `Downloading` job, observing `Completed`, surfacing async failure, returning existing failed/invalid states, rejecting offsets larger than object size, and allowing caller context cancellation without necessarily cancelling the background job.

## State and persistence behavior
The tests assert local file bytes are written with expected permissions and file-info offsets advance. Cleanup tests verify context cancellation, callback execution, context field clearing, and `doneCh` closure. CRC tests prove mismatched checksum deletes the local file and erases LRU state when CRC is enabled, while disabled CRC leaves tampered data and cache metadata intact.

## Dependencies and integration points
The suite uses fake storage, `storageutil`, random byte generation, `data.FileInfo`, `lru.Cache`, cache utilities, no-op metrics/tracing, and a weighted semaphore. It is tied to production locking because invariant checks are enabled and many tests run concurrent `Download` and `Invalidate` operations.

## Risks and edge cases
Several tests rely on timing, polling, or async cleanup ordering. A disabled CRC cancellation test is documented as flaky. Tests intentionally mutate object size to simulate failures, which is useful but not a production-realistic mutation path. Concurrent tests check outcomes but do not run under the Go race detector by default.

## Test signals
The file provides strong regression signals for status names, subscriber removal, callback exactly-once behavior, invalidation during active download, concurrent download/invalidate calls, CRC mismatch cleanup, context-canceled error classification, and O_DIRECT/non-O_DIRECT cache file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go -->
