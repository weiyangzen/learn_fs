<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go

## Purpose
This ogletest suite validates the parallel-download-specific behavior of `Job` while reusing the broader downloader test fixture. It exists to run analogous downloader scenarios with `EnableParallelDownloads=true` and to directly test range-map merging.

## Important fixtures and APIs
`parallelDownloaderTest` embeds `downloaderTest` and configures `FileCacheConfig` with parallel downloads enabled, `ParallelDownloadsPerFile=3`, `DownloadChunkSizeMb=3`, CRC enabled, and a 4 MiB write buffer. Tests call `downloadRange`, `parallelDownloadObjectToFile`, and `updateRangeMap` directly.

## Control flow and state behavior
`Test_downloadRange` downloads non-overlapping end, beginning, middle, and zero-byte ranges and checks file content at offsets. `Test_parallelDownloadObjectToFile` subscribes to an offset, downloads a 10 MiB object through the parallel path, verifies notification, local content, and file-info cache. Cancellation is tested by cancelling `job.cancelCtx` before invoking the parallel path. Range-map tests cover no existing ranges, extension at the end, extension at the start, filling a gap to merge two ranges, and inserting an isolated range.

## Dependencies and integration points
The tests rely on fake GCS storage, cache utilities, random byte generation, `data.FileSpec`, and production `updateStatusOffset` behavior. They interact with `rangeMap` directly to validate the internal representation used by subscriber progress notification.

## Risks and edge cases
The fake storage note in `job_test.go` about ranged reads is partly avoided here by parallel-specific paths, but fake storage behavior remains a dependency. Zero-byte range behavior is accepted as nil error, which may be important if future code rejects empty ranges. The tests check state after successful returns but do not assert exact goroutine count or semaphore acquisition.

## Test signals
Signals include correct offset writes for arbitrary ranges, full object reconstruction, subscriber offset notification, context-canceled error propagation, and bidirectional endpoint map invariants for merging contiguous downloaded ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go -->
