# sources/storage-engines/rocksdb/util/file_reader_writer_test.cc

Purpose: broad file reader/writer behavior test suite covering `WritableFileWriter`, readahead readers, line reader, checksum handoff, error notification, and I/O priority propagation.

Important tests: `RangeSync` validates bytes-per-sync aligned range sync scheduling. `IncrementalBuffer`, `AlignedBufferedWrites`, and `BufferWithZeroCapacityDirectIO` cover buffering/direct I/O constraints. `AppendWithChecksum`, `AppendVerifyNoChecksum`, and `AppendWithChecksumRateLimiter` exercise CRC32C append verification/handoff with fault-injection FS and rate limiting. `AppendStatusReturn` checks append error propagation. Readahead random/sequential parameterized tests validate empty, short, long, and over-readahead reads. `LineFileReaderTest` validates line counting and injected read errors. `IOErrorNotification` checks listener callbacks. `WritableFileWriterIOPriorityTest` checks priority propagation across operations.

Control flow: many tests define local fake `FSWritableFile` implementations to assert calls and simulate errors. DB-backed tests use `DBTestBase`, `FaultInjectionTestFS`, and `WritableFileWriter`. Parameterized tests instantiate multiple readahead sizes.

State and persistence: uses temporary DB/test files, memory strings, injected FS state, and listener counters. It verifies behavior that affects persisted file contents and checksums but does not define new storage formats.

Dependencies and integration: integrates file system abstractions, DB options, CRC32C, rate limiter, event listeners, mock env, string test sources/sinks, and sync point fault injection.

Risks: fake file implementations may not capture all filesystem behavior. Some tests depend on random data but fixed seeds. Fork/process lock behavior is not here; that is in `filelock_test.cc`.

Test signals: strong regression signal for file I/O wrappers, buffering, read-ahead, checksum handoff, and listener semantics.
