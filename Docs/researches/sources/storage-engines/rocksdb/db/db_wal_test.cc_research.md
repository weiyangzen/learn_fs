# sources/storage-engines/rocksdb/db/db_wal_test.cc

## Purpose
`db_wal_test.cc` is RocksDB's DB-layer regression suite for write-ahead log creation, replay, syncing, recycling, recovery-mode semantics, WAL tracking, and precreated future WAL files. It is test code, but it acts as a detailed executable specification for how user writes move between memtables, WAL files, SST/blob files, MANIFEST WAL metadata, and recovery.

The suite covers normal reopen and crash-recovery behavior, disabled-WAL writes, multi-column-family replay, timestamped keys, blob-enabled recovery flushes, WAL checksum handoff, `SyncWAL` concurrency and failure paths, preallocation/truncation behavior, `avoid_flush_during_recovery`, corruption handling under every `WALRecoveryMode`, WAL holes tracked through the MANIFEST, and async WAL precreation races.

## Important APIs, Types, and Functions
The core fixture is `DBWALTestBase : public DBTestBase`, constructed with `env_do_fsync=true` so tests exercise durable filesystem behavior. It adds `ListWalNumbers()`, `CreateEmptyWal()`, and `CreateWalWithContents()` helpers for direct WAL file inspection and synthesis. On POSIX/fallocate builds it also provides `IsFallocateSupported()`, `GetAllocatedFileSize()`, and `ShouldSkipAllocationCheck()` to validate physical preallocation without false failures on filesystems such as btrfs, zfs, tmpfs, and overlayfs.

`DBWALTest` is the main fixture. `EnrichedSpecialEnv` extends `SpecialEnv` to count WAL deletions, intentionally skip the first WAL delete, and detect whether recovery reopens a deleted WAL or observes gaps. `DBWALTestWithEnrichedEnv` installs that environment and enables 2PC for the skipped-deletion recovery test.

Timestamp coverage uses `DBWALTestWithTimestamp`, which derives from `DBBasicTestWithTimestampBase` and `WithParamInterface<test::UserDefinedTimestampTestMode>`. Its helpers open timestamp-aware column families, write timestamped values through `DB::Put`, and verify `DB::Get` returns both value and timestamp. This fixture validates WAL replay when user-defined timestamps are persisted, stripped, enabled, or disabled across reopen.

`RecoveryTestHelper` is the main synthetic-WAL generator. It writes a fixed number of numbered WAL files using `WritableFileWriter`, `log::Writer`, `WriteBatchInternal::SetSequence`, `VersionSet::SetLastSequence`, and optional WAL compression. It can count recovered keys and corrupt or truncate a target WAL at proportional offsets. Parameterized fixtures combine corruption style, corruption offset, target WAL file, compression type, WAL tracking, and recovery mode.

Other local test-only types include `DBRecoveryTestBlobError`, which injects blob-file builder failures during recovery; `DBWALTrackAndVerifyWALsWithParamsTest`, which runs WAL-hole scenarios across all recovery modes; `DBWALTestWithParams` and `DBWALTestWithParamsVaryingRecoveryMode`, which drive the corruption matrix; and small filesystem wrappers used to fail `Sync`, hide WALs from directory listings, or inject retryable write/metadata errors.

Major RocksDB APIs exercised include `DB::Open`, `DB::OpenForReadOnly`, `Reopen`, `TryReopen`, `CreateAndReopenWithCF`, `ReopenWithColumnFamilies`, `Put`, `Write`, `Merge`, `Flush`, `FlushWAL`, `SyncWAL`, `LockWAL`, `UnlockWAL`, `GetSortedWalFiles`, `GetCurrentWalFile`, `TEST_SwitchWAL`, `TEST_SwitchMemtable`, `TEST_FlushMemTable`, `PauseBackgroundWork`, `ContinueBackgroundWork`, `Resume`, `IngestExternalFile`, and internal inspection through `DBImpl`, `VersionSet`, `ColumnFamilyData`, `VersionStorageInfo`, `InternalStats`, and `FileMetaData`.

## Control Flow
Most tests follow a write/reopen/assert shape. They create a DB, write keys with different WAL options, optionally flush or force WAL rotation, reopen with the same or changed options, and assert key visibility, WAL counts, SST/blob counts, status codes, internal metadata, or statistics counters. Many tests loop over `ChangeWalOptions()` so the same behavior is checked across the repository's WAL option matrix.

The early tests establish baseline semantics. `WAL`, `Recover`, and `RollLog` prove data survives reopen when writes are mixed with `disableWAL` as long as persistence is otherwise guaranteed. `SyncWALNotBlockWrite` and `SyncWALNotWaitWrite` use `SyncPoint` ordering and background threads to ensure `SyncWAL()` does not unnecessarily block unrelated writes or wait for an in-flight append. `SkipDeletedWALs` verifies recovery skips already-obsolete WALs even if the environment failed to delete one, avoiding false gaps.

Timestamp tests reopen column families with and without `avoid_flush_during_recovery`, inspect SST metadata, and verify timestamped reads. They prove WAL records retain user-defined timestamps independently of whether timestamps are later persisted to SSTs, and that opening a CF while enabling or disabling timestamp support handles mixed WAL timestamp sizes.

Recovery-with-output-file tests cover replay that flushes memtables to SST/blob files. `RecoverWithTableHandle` checks whether recovered table readers are preloaded depending on `max_open_files`. `RecoverWithBlob` and `RecoverWithBlobMultiSST` reopen with blob files enabled after writing normal WAL entries, then assert recovery creates table/blob pairs, correct key bounds, blob counters, and compaction stats. `RecoverWithBlobError` injects failures in blob writing and verifies partial SST/blob outputs are cleaned up.

WAL metadata and file lifecycle tests inspect `GetSortedWalFiles`, `GetCurrentWalFile`, full purge behavior, WAL locking, empty logs, recycled logs, backup/restore of log directories, and WAL cleanup across column families. The full-purge tests force races where a WAL is recyclable or pending reuse and ensure obsolete-file cleanup cannot delete a still-needed log. The lock test ensures `LockWAL()` stops writes and async flushes until unlocked.

The central corruption matrix uses `RecoveryTestHelper` to generate many WALs, corrupt or truncate one of them, set `wal_recovery_mode`, and reopen. The tests encode the intended contract: `kTolerateCorruptedTailRecords` accepts truncated tails but rejects interior corruption, `kAbsoluteConsistency` rejects any corruption or WAL/SST inconsistency, `kPointInTimeRecovery` opens at the prefix before the first error, and `kSkipAnyCorruptedRecords` opens while skipping bad records and recovering later valid data where possible. Compression variants cover uncompressed and ZSTD WALs.

`avoid_flush_during_recovery` tests branch the recovery path between replaying into memtables and flushing recovered memtables to SSTs. They validate table-file counts, WAL retention after deferred flush, repeated reopens without flush, multi-CF replay across multiple WALs, corruption followed by appends, and restored total-WAL-size accounting that can later trigger WAL-full flushes.

The late tests focus on edge cases and recent async WAL features. POSIX/fallocate tests validate preallocated tail truncation after recovery with and without recovery flush, empty WAL truncation, and read-only recovery leaving allocated size unchanged. MANIFEST-tracking tests verify missing WALs are detected, obsolete WALs synced during a manifest rollover do not cause false missing-WAL corruption, and a WAL present in the MANIFEST but hidden from sorted WAL listing returns an error. Async WAL precreate tests force wait/no-wait consumption, recovery with an actual empty future WAL, cleanup on start failure, fallback after background precreate failure, read-only handling of empty future WALs, and recovery tolerance for hand-created future empty WALs.

## State and Persistence Behavior
The file directly exercises persistence of WAL records, WAL file numbers, WAL sizes, log directory contents, recycled WALs, preallocated blocks, MANIFEST WAL-add/delete metadata, column-family log numbers, sequence numbers, memtable contents, flushed SSTs, blob files, table readers, blob-file stats, and internal background-error state.

WAL replay is expected to preserve sequence-number truth even when some writes used `disableWAL`. `PartOfWritesWithWALDisabled` protects against replay code inventing contiguous sequence numbers from the first log record, which would make later WAL-enabled updates appear older than flushed data.

WAL deletion and recycling state is guarded carefully. Obsolete WALs can be skipped during recovery even when deletion failed, but non-obsolete holes must be detected when `track_and_verify_wals` or `track_and_verify_wals_in_manifest` is enabled. Recycled WAL tests guard against extra bytes from an old incarnation being replayed after a crash; one disabled test documents a known failing point-in-time case involving recycled WAL data, snapshots, and external SST ingestion.

Recovery flush policy is observable through SST/blob counts. With `avoid_flush_during_recovery=false`, recovered memtables are flushed and table/blob metadata is installed during open. With it set to true, replayed state remains in memory, old WALs remain live until a later flush, and total log size must still be restored so `max_total_wal_size` can trigger future flushes correctly. `allow_2pc` forces a flush despite `avoid_flush_during_recovery=true` in one test.

Preallocation state matters separately from logical WAL size. The POSIX tests distinguish `SizeFileBytes()` from allocated disk blocks and verify recovery truncates unused preallocated tails for writable opens, including empty WALs and crash-loop windows before deletion, while read-only opens must not modify file allocation.

Async WAL precreation introduces "future" zero-byte WALs that are not logical logs yet. The tests specify that foreground rotation must consume a ready precreated file, wait for a pending one, delete an unpublished file if WAL start fails, fall back to synchronous creation after background failure, and tolerate empty future WALs during read-only open and recovery without reporting WAL-chain or MANIFEST-tracking corruption.

## Dependencies and Integration Points
The file depends heavily on RocksDB test infrastructure from `db/db_test_util.h`, timestamp helpers from `db/db_with_timestamp_test_util.h`, option sanitization from `options/options_helper.h`, `test_util/sync_point.h`, and fault-injection wrappers from `utilities/fault_injection_env.h` and `utilities/fault_injection_fs.h`.

It integrates with WAL internals through `LogFileName`, `ParseFileName`, `log::Writer`, `WritableFileWriter`, `WalManager`, `VectorLogPtr`, `VectorWalPtr`, WAL compression records, `WriteBatchInternal`, `WriteOptions::disableWAL`, `WriteOptions::sync`, `manual_wal_flush`, and `DBImpl` test hooks such as `TEST_LogfileNumber()` and `TEST_GetCurrentLogNumber()`.

Recovery and metadata integration points include `VersionSet`, MANIFEST writes, `track_and_verify_wals`, `track_and_verify_wals_in_manifest`, `WalSet`, `FindObsoleteFiles`, `PurgeObsoleteFiles`, `MemTableList::TryInstallMemtableFlushResults`, `VersionSet::LogAndApply`, blob file builders, compaction stats, background flush scheduling, retryable background IO recovery, and `ErrorHandler` behavior exposed through `TEST_GetBGError()` and `TEST_IsRecoveryInProgress()`.

Filesystem integration is broad: POSIX `stat`/`statfs`/`fallocate`, `Env` file creation/deletion/reopen APIs, composite environments, `FileSystemWrapper`, `FSWritableFileOwnerWrapper`, checksum handoff, directory listing manipulation, file truncation/corruption helpers, injected write/sync/metadata errors, and platform-specific Windows truncation handling.

## Risks
The suite is sensitive to exact internal synchronization points and file-number ordering. Refactors that rename `SyncPoint` labels, change when a WAL is marked obsolete, or adjust manifest write timing can break tests even when the public API remains stable. Those failures are still useful because they often signal a changed persistence interleaving that needs a new explicit contract.

Recovery-mode behavior is high risk because the same corruption can be accepted, truncated to a prefix, skipped, or rejected depending on `WALRecoveryMode`, WAL tracking, and compression. Small changes in log-fragment boundaries or compression checksums can alter expected recovered row counts; tests therefore assert ranges and prefix properties rather than exact counts in several places.

WAL tracking in the MANIFEST is easy to make too strict or too lax. Too strict produces false missing-WAL corruption for obsolete, recycled, hidden, or empty future WALs; too lax can hide real WAL holes by number, sequence number, or size. The tests cover both sides, including read-only and async-precreated WAL cases.

`avoid_flush_during_recovery` interacts with memory accounting, WAL retention, flush triggers, 2PC, blob files, and corruption recovery. Regressions can manifest as leaked WALs, missing later flushes, duplicate sequence numbers, unexpected SST counts, or stale log-size accounting rather than simple missing keys.

Platform and environment assumptions are explicit risks. Preallocation assertions depend on POSIX/fallocate behavior and filesystem allocation reporting, so the file skips or softens checks for memory/encrypted environments and filesystems with known reporting differences. Checksum handoff, compression, direct file corruption, and background scheduling also depend on the active test environment.

Async WAL precreation adds concurrency hazards around ownership of unopened or unpublished files. A failed start must delete the future WAL outside the DB mutex, foreground switching must not skip WAL numbers while waiting for a pending file, and recovery must distinguish a valid empty future WAL from a missing or corrupt tracked WAL.

## Test Signals
Primary success signals are passing `db_wal_test` across the normal `ChangeWalOptions()` matrix and the parameterized recovery matrices. Important status expectations include `ASSERT_OK` for valid reopen/recovery paths, `ASSERT_NOK` or corruption status for absolute-consistency failures, `IsIncomplete()` while WAL is locked, fatal background error after manual WAL flush write failure, and no recovery-in-progress state for direct WAL write errors.

Data-integrity signals include keys surviving reopen, disabled-WAL writes being visible only when persisted by flush or surrounding recovery semantics, timestamped reads returning the correct historical value and timestamp, blob recovery preserving values and producing matching table/blob metadata, and point-in-time recovery returning a prefix without resurrecting records after the first unrecoverable error.

File and metadata signals include expected WAL counts from `GetSortedWalFiles`, current WAL metadata from `GetCurrentWalFile`, table/blob file counts after recovery flushes, deletion of partial files after failed blob recovery, WAL deletion counts from `EnrichedSpecialEnv`, MANIFEST-tracked WAL hole detection, obsolete/recycled WAL preservation during purge races, and file allocation shrinking after preallocation truncation.

Concurrency signals come from `SyncPoint`-controlled tests where `SyncWAL`, background flush, WAL reuse, manifest rollover, retryable IO recovery, and async precreation are forced into specific interleavings. These tests are especially valuable because they assert that writes continue, foreground switch waits only when required, obsolete WAL metadata remains consistent, and reopen succeeds after the race.

Statistics and internal-state checks provide additional signals: `WAL_PRECREATE_HIT`, `WAL_PRECREATE_WAITED`, `WAL_PRECREATE_MISS`, and `WAL_PRECREATE_FAILED` counters distinguish async precreate paths; `InternalStats` compaction bytes include blob bytes during recovery flush; `GetFullHistoryTsLow` reflects timestamp stripping; and `TEST_GetBGError()` confirms WAL write failures are treated as fatal rather than recoverable background IO errors.
