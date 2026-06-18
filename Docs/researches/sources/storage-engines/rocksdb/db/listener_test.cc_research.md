# sources/storage-engines/rocksdb/db/listener_test.cc

## Purpose

`listener_test.cc` is a RocksDB test suite for `EventListener` callback behavior. It validates callback ordering, callback payload completeness, thread ids, table properties, blob metadata, file operation notifications, background error suppression, shutdown notification semantics, column-family handle deletion notifications, and background job pressure snapshots.

The file is behavioral test code rather than production logic. It creates small DBs and column families, forces flushes/compactions/blob garbage collection, injects filesystem failures, blocks background jobs with sync points or sleeping tasks, and asserts listener-observed data against DB metadata.

## Important APIs, types, and functions

- `EventListenerTest` derives from `DBTestBase` and provides `BlobStr()` for generating blob index values plus a 110 KB write-buffer constant.
- `TestPropertiesCollector` and `TestPropertiesCollectorFactory` attach user-collected table properties used by listener assertions.
- `TestCompactionListener` checks `OnCompactionCompleted` payloads: input/output file info, file levels/numbers, table properties, thread id, DB pointer, and oldest blob file number.
- `TestCompactionPreCommitListener` verifies `OnCompactionBegin`, `OnCompactionPreCommit`, and `OnCompactionCompleted` ordering and checks that input files are still marked `being_compacted` at pre-commit time.
- `TestDBShutdownBeginListener` verifies shutdown callback count and DB pointer for cancel/close and failed open.
- `TestFlushListener` checks `OnTableFileCreated` and `OnFlushCompleted` payloads, thread status, slowdown/stop flags, table properties, file number, CF id/name, and oldest blob file number.
- `TableFileCreationListener` validates started/created/failure callbacks for flush and compaction table files, including injected filesystem failures and aborted empty output files.
- `BackgroundErrorListener` suppresses the first background error and lets retry succeed.
- `TestFileOperationListener` opts into file I/O notifications and counts read/write/flush/close/sync/truncate callbacks, including blob-file-specific counts.
- `BlobDBJobLevelEventListenerTest` checks blob file addition and garbage info in flush/compaction job-level callbacks and `CompactFiles()` output.
- `BlobDBFileLevelEventListener` checks blob file started/created/deleted callbacks.
- `BackgroundJobPressureTestListener` records background job pressure snapshots for later invariant checks.

## Control flow

Each `TEST_F` configures `Options`, installs one or more listeners, opens or reopens a test DB, performs writes, flushes, compactions, `CompactFiles()`, close/reopen, or failure injection, then checks listener state. Tests use `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, and `TEST_WaitForBackgroundWork()` to avoid racing asynchronous callbacks.

Compaction tests create enough L0 files or manual compactions to force callbacks and reason codes. Sync points enforce ordering for pre-commit notification. Flush tests use multiple column families and table property collectors to verify callback sequence and payload. Multi-DB tests install many listeners across several DBs and verify callback ordering by column family and DB.

Failure tests use `FaultInjectionTestFS`, `SpecialEnv::drop_writes_`, and a custom `FileSystemWrapper` to make open, flush, or compaction fail, then assert notification counts and statuses. Blob tests enable blob files and garbage collection, then flush/compact to force blob additions, garbage records, file-level creation, and deletion notifications. Background pressure tests block low-priority compaction work, build L0 pressure through flushes, then unblock compaction and verify pressure rises and falls.

## State and persistence behavior

The test DB writes real SST, WAL, MANIFEST, and blob files under the test directory, but only as fixtures. Listener instances store observed callback state in vectors, atomics, counters, mutex-protected fields, and statuses. Some tests intentionally close and reopen DBs to verify recovery file reads and shutdown semantics.

The suite checks persistent metadata indirectly by comparing callback file numbers and blob file metadata against `TEST_GetFilesMetaData()`, `VersionStorageInfo`, table properties, and column-family metadata. It also verifies user-collected properties survive into listener payloads.

## Dependencies and integration points

The file depends on RocksDB DB test utilities, DBImpl internals, `VersionSet`, blob index encoding, write batch internals, file naming helpers, statistics/perf context headers, cache/table/options APIs, sync points, special/fault-injection environments, rate limiter utilities, and merge operator utilities.

It integrates with many EventListener hooks: compaction begin/pre-commit/completed, DB shutdown begin, table file creation started/created, flush completed, memtable sealed, column-family handle deletion started, background error, file operation finish callbacks, blob file creation/deletion, and background job pressure changed.

## Risks and edge cases

- Listener callbacks can run asynchronously on background threads. Tests must wait for background work before reading listener state; the file contains several explicit waits for this reason.
- Some listener implementations use mutexes, but not all counters are protected in the same way. Tests are written around expected callback sequencing; future parallelism changes may require stronger synchronization.
- `TestFlushListener` assumes only one flush at a time and stores a single previous table creation info object.
- Callback assertions that inspect `DBTestBase::db_` are skipped or guarded for multi-DB/close cases because the DB pointer can differ or be closing.
- Failure injection around filesystem activity and background retries is timing-sensitive; sync points and mock sleep are used to stabilize expected behavior.
- The tests assert `kUnknownFileChecksum` and `kUnknownFileChecksumFuncName`, so enabling real file checksums in these paths would require updating expected listener payloads.
- Background job pressure tests depend on scheduler behavior and L0 thresholds; changes to compaction scheduling or pressure semantics can break expectations.

## Test signals

This file is itself the test signal for listener behavior. It covers single and multi-CF flush/compaction, multiple DBs and listeners, compaction reasons for level/universal/FIFO/manual compactions, table creation success/failure/aborted outputs, memtable sealing sequence bounds, background error suppression and retry, file I/O callback opt-in, manifest reads during recovery, blob job and file callbacks, `CompactFiles()` blob output reporting, shutdown notifications on cancel/close/failed open, and background job pressure invariants.
