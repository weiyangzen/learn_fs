# sources/storage-engines/rocksdb/file/file_prefetch_buffer.cc

## Purpose
`file_prefetch_buffer.cc` implements `FilePrefetchBuffer`, the reusable buffering and readahead engine used for table reads, user scans, compaction reads, and explicit/implicit prefetch. It supports synchronous reads, asynchronous reads with polling/abort, overlap buffers, filesystem-owned buffer reuse, readahead-size tuning, and statistics.

## Important APIs and control flow
`Prefetch()` is the simple single-buffer synchronous path. `TryReadFromCache()` delegates to `TryReadFromCacheUntracked()`, which checks min-offset tracking, explicit async request state, buffer coverage, implicit sequential-read eligibility, and calls `PrefetchInternal()` on misses or partial hits. `PrefetchAsync()` submits explicit async reads, optionally fills `result` immediately from existing data, resets stale async work, and returns `TryAgain` when the caller should poll via a later read.

`PrefetchInternal()` is the central path. It aborts outdated IO, clears outdated buffers, handles overlapping data across async buffers or filesystem-owned sync buffers, polls completed async reads, determines read spans via `ReadAheadSizeTuning()`, schedules remaining async buffers with `PrefetchRemBuffers()`, performs a synchronous `Read()` when necessary, and copies partial data into `overlap_buf_`.

`ReadAsync()` uses `RandomAccessFileReader::ReadAsync()` with `PrefetchAsyncCallback()` and falls back to synchronous read on `NotSupported`. `PollIfNeeded()`, `AbortOutdatedIO()`, and `AbortAllIOs()` manage filesystem async handles. `ReadAheadSizeTuning()` aligns offsets, invokes the optional cache-aware callback, trims already-prefetched ranges, prepares buffers, and records trimming stats.

## State, persistence, and integration
The implementation has no persistent state beyond in-memory buffers. It integrates with `RandomAccessFileReader`, `FileSystem::Poll`/`AbortIO`, direct-I/O alignment, optional `FSSupportedOps::kFSBuffer`, `IOOptions`, `Statistics` histograms/tickers, `StopWatch`, and sync points for fault injection.

## Risks and test signals
The code is sensitive to offset arithmetic, alignment, EOF/truncated reads, async callback races, stale handles, and overlap-buffer sizing. `async_read_in_progress_` is used as a main-thread coordination flag rather than a general mutex. `FSBufferDirectRead()` reuses filesystem buffers only for single-buffer non-direct reads, and prefetch explicitly disables that optimization in one path due to overflow risk. Test signals should include direct/non-direct IO, mmap exclusion, async supported/unsupported, Poll failure injection, non-sequential reads aborting stale IO, overlap across two buffers, cache-tuned trimming, stat counters, and sanitizer runs.
