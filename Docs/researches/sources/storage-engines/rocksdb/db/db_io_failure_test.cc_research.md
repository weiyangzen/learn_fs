# sources/storage-engines/rocksdb/db/db_io_failure_test.cc

## Purpose

This file is a GoogleTest suite for RocksDB database behavior under injected file-system and I/O failures. It exercises two broad classes of behavior: write-side failures from `SpecialEnv` flags and `SyncPoint` callbacks, and read-side corruption/retry behavior through a custom `FileSystemWrapper`. The tests are regression-oriented: they verify that failed flushes/compactions/manifest writes do not lose committed data, that paranoid mode blocks later writes after serious background failures, and that corruption retry counters are updated only when `verify_and_reconstruct_read` support is advertised.

## Important APIs, types, and functions

`CorruptionFS` wraps a target `FileSystem` and injects corruption into reads. It overrides `NewRandomAccessFile`, `NewSequentialFile`, `NewWritableFile`, and `SupportedOps`. It tracks a corruption trigger count, the corrupted filename and byte range, and a deterministic `Random` generator. `SetCorruptionTrigger()` resets the read counter and arms the next corruption. `MaybeResetOverlapWithCorruptedChunk()` clears the corrupted file marker when a verification/reconstruction read overlaps the corrupted byte range. `VerifyRetry()` confirms a corruption was injected and later repaired by a retry path.

`CorruptionRandomAccessFile` and `CorruptionSequentialFile` are nested wrappers that corrupt successful reads unless `IOOptions::verify_and_reconstruct_read` is set. The random-access wrapper also implements `MultiRead()` with two allocation modes: normal caller scratch buffers and an `FSAllocationPtr`-backed buffer path when the wrapped FS advertises `kFSBuffer`.

`DBIOFailureTest` derives from `DBTestBase` and uses `SpecialEnv` through `env_` to inject drop writes, no space, non-writable filesystem, log, manifest, sync, range sync, and close errors.

`DBIOCorruptionTest` derives from `DBIOFailureTest` and parameterizes three booleans: use FS-provided buffer, use async read options, and advertise retry support through `kVerifyAndReconstructRead`. Its constructor installs `CorruptionFS` in a composite Env, configures statistics, disables auto compactions, and uses a block-based table factory.

## Control flow and scenarios

The early `DBIOFailureTest` cases drive normal writes and flushes to create durable data, then enable an injected failure and assert the DB's returned status, background error counters, write availability, and post-reopen data visibility. `DropWrites` loops over compaction option variants, forces dropped writes during compaction, expects background errors to accumulate, then ensures file count growth remains bounded and compaction sleeps occurred. `DropWritesFlush` checks flush failure increments `rocksdb.background-errors`. `NoSpaceCompactRange` verifies `CompactRange` propagates an `IOError` with `NoSpace`.

`ManifestWriteError` covers a subtle persistence failure: a compaction output may be written to the MANIFEST but fail sync, or the manifest write itself may fail. The test checks data remains readable, paranoid mode blocks writes, reopening with paranoid disabled can recover, and subsequent writes work when safe.

`PutFailsParanoid` verifies that WAL write errors poison future writes only when `paranoid_checks` is true.

The `#if !(defined NDEBUG) || !defined(OS_WIN)` block uses `SyncPoint` callbacks on `SpecialEnv::SStableFile::{RangeSync,Close,Sync}` for both flush and compaction paths. Each test injects an error on the first callback, waits for flush or compaction, asserts the exact error message, confirms later writes are rejected in paranoid mode, and reopens to verify committed data survived.

The parameterized corruption tests inject read corruption at different layers. `GetReadCorruptionRetry`, `IterReadCorruptionRetry`, `MultiGetReadCorruptionRetry`, `CompactionReadCorruptionRetry`, `FlushReadCorruptionRetry`, `ManifestCorruptionRetry`, `FooterReadCorruptionRetry`, `TablePropertiesCorruptionRetry`, and `DBOpenReadCorruptionRetry` compare retry-enabled and retry-disabled behavior through status checks plus `FILE_READ_CORRUPTION_RETRY_COUNT` and `FILE_READ_CORRUPTION_RETRY_SUCCESS_COUNT` tickers.

## State and persistence behavior

The tests intentionally move data through memtable, SST, manifest, reopen, and compaction states. They validate that failures during output file close/sync/range sync do not publish partial SST state as durable truth. Manifest failure tests protect the VersionSet contract that reopened DB state must not point to a deleted or unpublished compaction output. Corruption retry tests validate that the read path can reconstruct a corrupted read without mutating logical DB contents.

`CorruptionFS` state is protected by `port::Mutex`. Its destructor asserts that armed corruption was either reset or triggered into a non-empty corrupted chunk, helping catch tests that forget to exercise the injected condition. Global `SyncPoint` callbacks mutate process-wide state, so tests disable processing after each injection; footer and table properties tests also clear callbacks.

## Dependencies and integration points

The suite depends on `DBTestBase`, `SpecialEnv`, `SyncPoint`, `BlockBasedTableFactory`, `NewBloomFilterPolicy`, `test::NewSpecialSkipListFactory`, RocksDB `Statistics`, and Env/FileSystem abstractions. It integrates with the DB background error machinery, flush and compaction scheduling, MANIFEST recovery, table reader checksum paths, `MultiGet`, iterator scans, file footer/property reads, and file-system capability advertisement through `SupportedOps`.

## Risks and edge cases

The custom FS corrupts buffers returned by read calls; this is appropriate for tests but is sensitive to aliasing and buffer ownership, especially in the `MultiRead()` FS-buffer path. Tests using `SyncPoint` are global-state sensitive and must always disable or clear callbacks to avoid cross-test interference. Some assertions are platform/configuration gated because debug and Windows behavior differ. `GetReadCorruptionRetry` sets `ro.async_io` but calls `Get(ReadOptions(), ...)`, so that test does not actually exercise its async parameter in the same way as the iterator, compaction, and `MultiGet` tests. The corruption retry matrix still covers async elsewhere.

## Test signals

The file is itself the test signal for DB I/O failure handling. It asserts exact status classes (`IOError`, `Corruption`, `NoSpace`), background-error properties, retry ticker counts, data survival after reopen, and write blocking under paranoid checks. The parameter matrix combines FS buffer support, async I/O, and verify/reconstruct support to make sure corruption recovery is conditional on advertised capability rather than always attempted.
