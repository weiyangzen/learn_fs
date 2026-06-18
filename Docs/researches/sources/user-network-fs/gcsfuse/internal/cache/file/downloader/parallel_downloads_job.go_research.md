<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go

## Purpose
This file implements the parallel download mode for `Job`. It splits an object into configured byte ranges, fans those ranges out to worker goroutines, writes them into the cache file at fixed offsets, tracks contiguous downloaded ranges, updates file-info progress as the prefix becomes complete, and respects job cancellation plus manager-wide parallelism limits.

## Important APIs and functions
`downloadRange` opens a ranged GCS reader, copies bytes into a provided writer, captures metrics, optionally uses memory-aligned buffers for O_DIRECT, and returns the reader's read handle. `updateRangeMap` merges newly downloaded intervals and updates job status when a range starting at zero grows. `downloadOffsets` is the worker loop over `job.rangeChan`. `parallelDownloadObjectToFile` creates workers, feeds ranges, opportunistically starts additional workers when semaphore slots open, and delegates final error handling to `handleJobCompletion`.

## Control flow and state behavior
`parallelDownloadObjectToFile` sizes ranges by `DownloadChunkSizeMb`, starts up to `ParallelDownloadsPerFile` workers while reserving global semaphore tokens for workers after index zero, and publishes every object range to `rangeChan`. Each worker preserves its own GCS read handle across assigned ranges. In experimental default mode, progress is tracked inside `downloadRange` at `ReadChunkSize` granularity; otherwise `downloadOffsets` updates range completion after each full range. `updateRangeMap` stores bidirectional endpoints so left and right adjacent ranges can be merged cheaply.

## Dependencies and integration points
The file relies on `errgroup`, `gcs.ReadObjectRequest`, `data.ObjectRange`, cache utility aligned-copy support, logger, metrics, and the `Job` lock and file-info update mechanism from `job.go`. It uses `job.maxParallelismSem`, shared by all manager jobs, as the cross-file concurrency limiter.

## Risks and edge cases
Range-map correctness is critical because subscribers only know about contiguous data from offset zero. The first worker deliberately does not release/acquire the global semaphore, which ensures progress but means global max is not a hard cap on total goroutines. Closing `rangeChan` in `handleJobCompletion` assumes no sender continues after a context path returns. O_DIRECT errors can surface as non-context errors, so code joins `ctx.Err()` when cancellation is detected.

## Test signals
Parallel tests cover ranged content writing, full parallel object download, cancellation, range-map merge cases, read-handle propagation under concurrency, O_DIRECT disabled mode, object-size capping, and concurrent downloads across jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go -->
