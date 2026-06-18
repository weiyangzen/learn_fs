<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go

## Purpose
This file implements the core downloader `Job`, an asynchronous state machine that downloads one GCS object into one local cache file, updates file-info cache progress, notifies subscribers waiting for offsets, validates CRC, handles cancellation/invalidation, and chooses sequential or parallel download mode.

## Important APIs and types
`JobStatus` stores `Name`, `Err`, and contiguous downloaded `Offset`. Status names are `NotStarted`, `Downloading`, `Completed`, `Failed`, and `Invalid`. `NewJob` configures object, bucket, LRU cache, read size, cache file spec, removal callback, file-cache config, semaphore, metrics/tracing, and volume block size. Public APIs are `Download`, `GetStatus`, `Invalidate`, `IsParallelDownloadsEnabled`, and `IsExperimentalParallelDownloadsDefaultOn`.

## Control flow and state behavior
`Download` validates the requested offset, starts one background `downloadObjectAsync` from `NotStarted`, returns immediately or subscribes for offset progress, and surfaces terminal `Failed`/`Invalid`/`Completed` states. Subscribers are notified when status is failed, invalid, or has reached their offset. Sequential downloading opens ranged GCS readers with `NewReaderWithReadHandle`, copies in `ReadChunkSize` segments, propagates read handles between sequential ranges, and calls `updateStatusOffset` after each segment. `downloadObjectAsync` creates the cache file, delegates to sequential or parallel download, truncates final file size, validates CRC, marks completion, and always runs cleanup. Cleanup cancels context, invokes the manager callback once, clears context fields, and closes `doneCh`.

## State and persistence behavior
The local file is created/truncated before download. Progress is persisted in the shared `lru.Cache` by replacing the `data.FileInfo` value without changing LRU order; update failure due to missing entry is interpreted as invalidation during eviction. CRC mismatch erases file-info cache and truncates/removes the local file. `Invalidate` cancels an active download, blocks until the goroutine exits, marks the status invalid, removes the manager callback, and notifies subscribers.

## Dependencies and integration points
The job depends on `gcs.Bucket.NewReaderWithReadHandle`, cache `data.FileInfo`, `lru.Cache`, cache utilities for file creation and CRC, `locker`, logger, metrics/tracing, and semaphores shared by `JobManager`. Parallel and sparse behavior are implemented in companion files but share this struct's fields and locks.

## Risks and edge cases
The locking is subtle: `cancel` releases `job.mu` while waiting to avoid deadlock with the download goroutine. Subscriber notification can report `Downloading` with enough offset before final CRC validation, so callers must handle later terminal failure. `validateCRC` dereferences `job.object.CRC32C`; it relies on populated object metadata when CRC is enabled. O_DIRECT fallback handles invalid file-open errors, but platform-specific direct I/O behavior remains risky.

## Test signals
`job_test.go` covers state initialization, subscriber notification, offset updates, sequential download, `Download` state branches, cancellation, invalidation races, CRC cleanup, config helpers, and cache-file creation. `job_testify_test.go` verifies read-handle propagation with mocked GCS readers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go -->
