# sources/storage-engines/rocksdb/db/db_basic_test.cc

## Purpose
`db_basic_test.cc` is a broad RocksDB DB-layer regression suite. It exercises core `DB`/`DBImpl` behavior around opening, locking, read-only and compacted modes, flush/compaction, snapshots, column families, `MultiGet`, recovery, MANIFEST/WAL metadata, file checksums, deadline-aware IO, and close/open error handling.

The file is not production code, but it is an important behavioral specification for persistence and recovery contracts. Several tests target newer metadata optimizations, especially `optimize_manifest_for_recovery` and `reuse_manifest_on_open`, proving that clean reopen paths avoid unnecessary MANIFEST edits without breaking WAL replay, best-efforts recovery, two-phase commit, dropped column families, WAL tracking, or crash durability.

## Important APIs, Types, and Functions
The primary fixture is `DBBasicTest : public DBTestBase`, constructed with test directory `db_basic_test` and `env_do_fsync=false`. It relies on the large helper surface from `db/db_test_util.h`: `DestroyAndReopen`, `Reopen`, `TryReopen`, `CreateAndReopenWithCF`, `ReopenWithColumnFamilies`, `Put`, `Delete`, `SingleDelete`, `TimedPut`, `Merge`, `Flush`, `Get`, `MultiGet`, `MoveFilesToLevel`, `NumTableFilesAtLevel`, `AllEntriesFor`, `dbfull()`, `env_`, `dbname_`, and column family handles.

Local helper types include:

- `MyFlushBlockPolicy` and `MyFlushBlockPolicyFactory`, which force block boundaries every N keys for block-based table and `MultiGet` tests.
- `RecoveryOptimizationCounters`, which installs `SyncPoint` callbacks for skipped recovery edits: setup DB ID, per-CF edits, WAL deletion edits, and next-file-number edits.
- `TestEnv` and `TestEnv::TestLogger`, which verify logger close ownership and close error propagation.
- `DBMultiGetTestWithParam`, `DBMultiGetAsyncIOTest`, `DBBasicTestMultiGet`, `DBBasicTestWithParallelIO`, `DBBasicTestMultiGetDeadline`, `MultiGetPrefixExtractorTest`, `DBMultiGetRowCacheTest`, `DBBasicTestTrackWal`, `DBBasicTestDeadline`, `DBBlockChecksumTest`, and `BestEffortsRecoverIncompleteVersionTest`, which parameterize important option and IO matrices.
- `TableFileListener`, `FlushTableFileListener`, and `FlushBlobFileListener`, which collect generated SST/blob file paths by column family for recovery deletion/corruption tests.
- `DeadlineFS` and `DeadlineRandomAccessFile`, wrappers that verify `IOOptions::timeout` propagation and inject timed-out reads for `Get`, `MultiGet`, and iterator deadline behavior.
- `ChecksumCapturingFS`, which captures SST `FileOptions` checksum metadata to prove file checksums are passed into table open paths.

Major RocksDB APIs covered include `DB::Open`, read-only open paths, `DB::CreateColumnFamily`, `DB::CreateColumnFamilies`, `DB::DestroyColumnFamilyHandle`, `DB::GetDbSessionId`, `DB::GetDbIdentity`, `DB::SyncWAL`, `DB::FlushWAL`, `DB::GetLiveFiles`, `DB::GetLiveFilesStorageInfo`, `DB::VerifyFileChecksums`, `DB::CompactRange`, `DB::WaitForCompact`, `DB::GetSnapshot`/`ReleaseSnapshot`, iterator creation, `GetAllKeyVersions`, table factories, `BlockBasedTableOptions`, merge operators, file checksum generators, and WAL/manifest inspection via `VersionSet`.

## Control Flow
Most tests follow a setup-write-flush-close-reopen-assert pattern. Basic tests create data, optionally flush it to SSTs, close or reopen with changed options, and assert key visibility, status codes, file counts, metadata counters, or internal state.

The first large group drives MANIFEST recovery behavior. Tests run paired configurations with `optimize_manifest_for_recovery` off/on, attach `SyncPoint` callbacks around `VersionSet::ProcessManifestWrites:AddRecord` and `DBImpl::Recovery:SkippedNoopEdit:*`, and compare the number of emitted MANIFEST records. Other tests force dirty WAL replay, multi-CF reopen, synthetic high-number SST files, dropped CFs, `track_and_verify_wals_in_manifest`, `allow_2pc`, `best_efforts_recovery`, and runtime option changes before close.

The `reuse_manifest_on_open` group creates a flushed DB, closes it, reopens with append-mode MANIFEST reuse, then forces new metadata writes and checks the MANIFEST file number, writer size accounting, rotation on size caps, multi-CF append edits, best-efforts disablement, tail-corruption rejection, and composition with recovery-marker optimization.

The middle of the file branches into DB basics: read-only operations must reject writes, compacted DB mode must serve reads and `MultiGet` from compacted LSM layouts, level-count mismatches must fail open, flush and compaction must collapse obsolete entries correctly, snapshots must preserve historical values and snapshot metadata, and DB identity/session IDs must remain stable or change in the expected places.

The `MultiGet` section is a dense matrix. It tests empty inputs, simple and multi-CF reads, batched vs unbatched calls, sorted and unsorted input, duplicate keys, value-size soft limits, merges spanning memtable/L0/L1/L2, prefix bloom behavior, row cache, snapshots, persisted-tier reads under concurrent atomic flush, async IO/coroutine paths, io_uring disablement, direct IO, checksum mismatch, missing files, and parallel IO cache/read-count behavior.

The recovery section manipulates the on-disk DB directory directly: deleting `CURRENT`, MANIFESTs, SSTs, WALs, and blob files; corrupting table and MANIFEST contents; injecting VersionBuilder errors; and checking that best-efforts recovery salvages only safe files, retries multiple manifests, clears unsafe table-cache references, skips WAL replay when table files are missing, and preserves ability to write after recovery.

Deadline tests wrap the filesystem, set `ReadOptions::deadline` and `ReadOptions::io_timeout`, clear block cache to force IO, and increment injected delay positions until every read site that can time out has been covered. Final tests verify checksum APIs, logger creation failure, manifest write failure after sync, default CF handle ownership, disallowed memtable writes, and propagation of file checksum metadata through `FileOptions`.

## State and Persistence Behavior
Persistent state under test includes WAL files, MANIFEST records, `CURRENT`, SST and blob files, IDENTITY/DB IDs, session IDs, table file checksums, WAL tracking sets, next file numbers, column family metadata, snapshots, and live-file metadata.

`optimize_manifest_for_recovery` is expected to persist close-time WAL markers so a later clean reopen can skip no-op recovery edits. The tests define the safe boundaries: dirty WAL replay must still emit per-CF edits, WAL tracking must still emit required deletion/tracking records, best-efforts recovery must publish a fresh salvage MANIFEST/CURRENT, 2PC must not advance WAL retention, dropped CFs must not receive marker edits, and synthetic high-number files must still advance the next file number.

`reuse_manifest_on_open` changes how metadata persists after reopen. Instead of creating a fresh descriptor, RocksDB may append to the existing MANIFEST when the valid tail and mode allow it. The tests ensure append-mode writers adopt the existing on-disk size, still rotate when size caps demand it, skip reuse on tail garbage or best-efforts recovery, and keep recovered SSTs durable by syncing their directories before MANIFEST publication or append.

Recovery tests intentionally create incomplete persistence states. Best-efforts recovery may discard missing/corrupt SSTs and produce a reduced but consistent version, create a new empty DB when no MANIFEST exists and `create_if_missing=true`, or fail when `create_if_missing=false`. WAL replay is guarded so WAL records are not applied when table-file loss would make the version unsafe. Obsolete WAL tracking must not cause reopen failures after obsolete files are manually removed.

## Dependencies and Integration Points
The file integrates with RocksDB internals and test utilities rather than external services. Key dependencies are `db/db_test_util.h`, `options/options_helper.h`, `rocksdb/*` public option and API headers, block-based table reader/builder internals, `test_util/sync_point.h`, checksum helpers, random utilities, counted/fault-injection filesystems, and merge operators.

Integration points include `VersionSet`/MANIFEST processing, `DBImpl` recovery and close paths, `WritableFileWriter`, WAL tracking, table cache opening, block-based table filters/indexes, row cache, blob files, file checksum generators, filesystem wrappers, environment background thread scheduling, coroutine/async IO, io_uring selection through the local `RocksDbIOUringEnable` hook, and GoogleTest parameter instantiation.

## Risks
Because this is a very broad regression suite, tests can become sensitive to internal SyncPoint names, manifest record counts, file-number allocation, or option-derived behavior. Refactors in recovery or `VersionSet` can break tests without changing user-visible behavior unless the SyncPoint contracts are kept current.

The MANIFEST optimization tests guard high-risk persistence paths. Incorrectly skipping an edit can leave `CURRENT` stale, lose WAL-retention state, reuse file numbers, mishandle dropped CFs, or make 2PC recovery unsafe. Conversely, over-emitting edits regresses the optimization and is caught by record counters.

`MultiGet` coverage spans cache state, compression availability, async IO support, direct IO alignment, prefix filters, snapshots, and injected filesystem failures. These tests can be platform-sensitive and may require conditional bypasses for coroutine, io_uring, direct IO, mmap, or compression support.

Best-efforts recovery tests intentionally corrupt and delete files. Their expected data loss is part of the contract, so maintenance must distinguish tolerated salvage behavior from accidental replay of unsafe WAL data or dangling table-cache references.

Deadline tests use synthetic sleeps and tight timeout propagation assertions. Clock handling, cache warmup, filter reads, and file-open behavior can create false failures if IO paths change without updating the wrapper expectations.

## Test Signals
Strong signals from this file include successful `db_basic_test` runs across default and parameterized configurations, especially the optimization/reuse tests, `DBMultiGetTestWithParam`, `DBMultiGetAsyncIOTest` when coroutine support is enabled, `ParallelIO`, `DeadlineIO`, and `DBBasicTestDeadline`.

Important behavioral assertions are: open-lock conflicts return `IOError`; read-only DB rejects write/flush/WAL mutation APIs but serves reads; identities and sessions follow documented restart behavior; flush/compaction preserve snapshot-visible values while removing obsolete entries; `MultiGet` returns per-key statuses and values consistently across CFs, levels, merges, duplicates, snapshots, row cache, prefix bloom, soft limits, async IO, and injected IO failures; recovery salvage only keeps safe files; file checksums verify only when configured and are propagated to SST open options; and `disallow_memtable_writes` rejects writes and incompatible WAL recovery cleanly.
