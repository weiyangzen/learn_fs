# sources/storage-engines/rocksdb/file/prefetch_test.cc

## Purpose

`prefetch_test.cc` is an extensive integration and unit test suite for RocksDB prefetch behavior. It validates filesystem prefetch selection, `FilePrefetchBuffer`, tail prefetch during table open/verification, adaptive and implicit readahead, block cache interactions, iterator seek/scan behavior, async IO/io_uring paths, poll error propagation, IO tracing, and filesystem-buffer reuse.

## Important APIs, Types, and Fixtures

- `MockRandomAccessFile` wraps `FSRandomAccessFile`, optionally supports `Prefetch`, counts prefetch calls, and can force buffer alignment to 1.
- `MockFS` wraps a filesystem and returns `MockRandomAccessFile`; it exposes `ClearPrefetchCount`, `IsPrefetchCalled`, and `GetPrefetchCount`.
- `PrefetchTest` is a `DBTestBase` parameterized by filesystem-prefetch support and direct IO. It configures DB/table options and provides correctness helpers `VerifyScan` and `VerifySeekPrevSeek`.
- `PrefetchTailTest` extends `PrefetchTest` with helpers for tail-prefetch scenarios and partitioned index/filter options.
- `PrefetchTrimReadaheadTestParam` tests readahead trimming with different index shortening modes and auto-readahead settings.
- `PrefetchTest1` focuses on async seek parallelization and adaptive readahead.
- `FilePrefetchBufferTest` directly exercises `FilePrefetchBuffer` using a `RandomAccessFileReader`.
- `FSBufferPrefetchTest` tests buffer reuse and async/sync prefetch internals, including a custom `BufferReuseFS` that advertises `kFSBuffer`.

## Control Flow and State

The tests repeatedly build small RocksDB instances with deterministic keys and values, flush or compact to create SST layouts, then read through iterators or direct `FilePrefetchBuffer` calls while sync-point callbacks count internal events. The primary state observed is prefetch counters, RocksDB statistics histograms/tickers, perf context counters, buffer offsets/sizes, iterator validity/status, and file contents read from prefetch buffers.

Core scenarios include:

- Basic selection: when filesystem prefetch is supported and direct IO is disabled, RocksDB should call filesystem `Prefetch`; otherwise it should use `FilePrefetchBuffer`.
- Tail prefetch: table verification/open should use prefetched tails to reduce extra reads, and upgrade logic should handle missing manifest tail-size metadata without per-partition read explosion.
- Dynamic readahead settings: mutable `block_based_table_factory` options for max/initial auto readahead and number of file reads are refreshed and affect iterator prefetch behavior.
- Reseek heuristics: sequential block reads enable prefetch; non-sequential reads and single-block rereads do not; cached blocks can suppress or reduce readahead.
- Trimming: auto readahead is trimmed by `prefix_same_as_start` or iterate upper bound, recorded by `READAHEAD_TRIMMED`.
- Adaptive readahead: sequential scans carry readahead state across SST files; non-sequential moves fall back to initial size.
- Async IO: `ReadOptions::async_io`, io_uring availability, seek parallelization, extra prefetch on seek, async byte histograms, and fallback when io_uring is disabled are all validated.
- Error handling: injected `Poll()` IO errors must propagate to iterator status or direct `FilePrefetchBuffer` status and must not corrupt retry reads.
- Direct buffer tests: `FilePrefetchBuffer` tests validate alignment, overlap buffer reuse, useful-byte stats, sync fallback, compaction mode, and randomized read sequences.

## Dependencies and Integration Points

The suite touches DB internals, block-based table options, file prefetch buffer implementation, file utilities, filesystem wrappers, sync points, io tracer parser tooling when `GFLAGS` is enabled, direct IO test mocking, statistics, perf context, caches, compaction, flush, iterators, and Posix filesystem async behavior. Because it drives real DB operations, it is a broad integration signal for table readers, block cache, and storage-engine file IO.

## Risks and Edge Cases

- Many expectations depend on exact block layouts, data sizes, and partitioned index behavior; small production changes can require test updates.
- Tests often bypass when direct IO or async IO is unsupported, so platform coverage varies.
- Sync-point counters can be brittle if internal function names or call counts change.
- Some tests distinguish filesystem prefetch versus RocksDB buffer prefetch, which is sensitive to mock filesystem capability reporting.
- Async tests must handle io_uring fallback cleanly; false assumptions about async availability would cause flaky assertions.
- Direct internal buffer assertions are valuable but tightly coupled to `FilePrefetchBuffer` layout and alignment policy.

## Test Signals

This file is itself the test signal for the prefetch subsystem. It verifies correctness by comparing iterator output to baseline iterators, matching file content slices, checking IO statuses, and asserting statistics such as `TABLE_OPEN_PREFETCH_TAIL_READ_BYTES`, `COMPACTION_PREFETCH_BYTES`, `FILE_READ_*_MICROS`, `ASYNC_READ_BYTES`, `READ_ASYNC_MICROS`, `PREFETCH_HITS`, `PREFETCH_BYTES_USEFUL`, `PREFETCHED_BYTES_DISCARDED`, `READAHEAD_TRIMMED`, and block-cache miss counts.
