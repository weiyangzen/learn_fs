# sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.cc

## sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.cc

### Purpose

`db_impl_secondary.cc` implements RocksDB secondary-mode database behavior and the remote-compaction worker path built on top of it. A secondary DB shares the primary DB's storage, opens with a private `secondary_path_`, replays MANIFEST state through `ReactiveVersionSet`, optionally tails WALs into local memtables, exposes read APIs over the reconstructed state, and rejects normal mutation APIs at the header level. The same implementation is also used by `DB::OpenAndCompact()` to open primary metadata as a secondary, run a compaction into an output directory, and serialize a `CompactionServiceResult` without installing generated files into the source DB.

### Important APIs, Types, And Functions

- `DBImplSecondary::DBImplSecondary()` delegates to `DBImpl` in secondary/read-only-oriented mode, stores `secondary_path_`, and logs the secondary open.
- `Recover()` replays MANIFEST only via `ReactiveVersionSet::Recover()`, initializes `max_total_in_memory_state_`, and creates the default column-family handle.
- `FindNewLogNumbers()`, `MaybeInitLogReader()`, and `RecoverLogFiles()` discover WALs, cache `log::FragmentBufferedReader`s in `log_readers_`, verify timestamp-size metadata, and insert replayed batches into `column_family_memtables_`.
- `GetImpl()`, `NewIterator()`, `NewIteratorImpl()`, and `NewIterators()` provide point and iterator reads against the secondary's current SuperVersions. They validate user-defined timestamp compatibility, disallow snapshots/tailing iterators in secondary mode, and use `versions_->LastSequence()` as the read snapshot.
- `TryCatchUpWithPrimary()` is the explicit refresh operation: apply more MANIFEST records, replay WALs, install new SuperVersions for changed column families, and purge obsolete local references.
- `DB::OpenAsSecondary()` overloads and `DBImplSecondary::OpenAsSecondaryImpl()` construct the secondary DB, create a logger under the secondary path if needed, recover MANIFEST/WAL state, build requested column-family handles, and publish SuperVersions.
- Remote compaction helpers include `OpenAndCompact()`, `CompactWithoutInstallation()`, `InitializeCompactionWorkspace()`, `PrepareCompactionProgressState()`, `ParseCompactionProgressFile()`, `FinalizeCompactionProgressWriter()`, and cleanup helpers for progress and SST output files.

### Control Flow

Open-as-secondary first adapts options, warns when `max_open_files != -1` because the primary can delete files while the secondary still needs them, creates `DBImplSecondary`, replaces the version set with `ReactiveVersionSet`, initializes column-family memtable access, and locks the DB mutex for recovery. `Recover()` reads only MANIFEST state. `OpenAsSecondaryImpl()` then optionally calls `FindAndRecoverLogFiles()` when `recover_wal` is true; this is used for normal secondaries but skipped by `OpenAndCompact()` because remote compaction only needs installed LSM state, not unflushed WAL data.

Catch-up follows the same ordering. `TryCatchUpWithPrimary()` holds the mutex while `ReactiveVersionSet::ReadAndApply()` consumes new MANIFEST edits, logs updated level summaries, discovers WAL files, and replays any useful records. It then removes old immutable memtables for changed column families, installs fresh SuperVersions, drops the mutex, cleans job state, and separately runs obsolete-file discovery/purge for secondary-owned references.

WAL replay is careful about ordering and partial primary activity. `FindNewLogNumbers()` uses `versions_->min_log_number_to_keep()` and the lowest cached log reader to avoid assuming a newer WAL means older current WALs are closed. `RecoverLogFiles()` initializes readers for all candidate logs, marks WAL file numbers as used, decodes each record as a `WriteBatch`, verifies timestamp-size consistency against running column-family metadata, skips records whose sequence is already covered by L0 files, switches a column family's active memtable when replay moves to a new WAL, and updates `LastAllocatedSequence`, `LastPublishedSequence`, and `LastSequence` after successful inserts.

Reads are DBImpl-like but secondary-specific. Point lookups build a timestamp-aware `LookupKey` at `versions_->LastSequence()`, check mutable and immutable memtables first, optionally resolve blob-backed memtable values through `BlobFetcher`, then consult current SST versions. Iterators reject tailing and explicit snapshots, acquire referenced SuperVersions, check timestamp history collapse, and call `NewArenaWrappedDbIterator()` with `allow_mark_memtable_for_flush=false`.

`OpenAndCompact()` deserializes `CompactionServiceInput`, loads the primary options file, applies `CompactionServiceOptionsOverride`, opens only default plus target column family as a secondary with WAL recovery disabled, locates the target handle, runs `CompactWithoutInstallation()`, writes the result, and closes handles/DB. The compaction path builds a compaction from input file numbers, prepares an output directory in `secondary_path_`, optionally loads persisted progress for resumption, constructs `CompactionServiceCompactionJob`, runs it outside the mutex, cleans up metadata, records resumed bytes, and returns the compaction status in the result.

### State And Persistence Behavior

The secondary's durable input state is owned by the primary: MANIFEST, SSTs, WALs, OPTIONS, and blob files. The secondary maintains local in-memory state in `ReactiveVersionSet`, SuperVersions, `log_readers_`, `cfd_to_current_log_`, memtables rebuilt from WALs, and `compaction_progress_`. It does not own normal DB tables/logs (`OwnTablesAndLogs()` returns false), and `FlushForGetLiveFiles()` is a no-op.

The `secondary_path_` is persistent workspace for secondary logs and remote-compaction output. Remote compaction can create table files, compaction-progress log files, temporary progress files, and a local info log there. Resumable compaction persists `VersionEdit` records containing `SubcompactionProgress` to a log-style progress file, syncs the initial progress, renames from temp to final progress filename, then reopens a writer on the finalized file. Startup scans the workspace once, keeps only the newest progress file when resuming, deletes old/temp progress files, preserves output files referenced by parsed progress, and removes extra SSTs.

### Dependencies And Integration Points

This file is tightly coupled to `DBImpl`, `ReactiveVersionSet`, `ColumnFamilyData`, `SuperVersion`, `WriteBatchInternal`, WAL `log::Reader`/`FragmentBufferedReader`, `WritableFileWriter`, `VersionEdit`, `CompactionServiceInput/Result`, `CompactionServiceCompactionJob`, and RocksDB file naming helpers. Public integration surfaces are declared in `include/rocksdb/db.h` and exposed through the C API in `db/c.cc`. Tests and sync points are concentrated in `db_secondary_test.cc`, with named sync points around WAL catch-up and OpenAndCompact option loading/opening.

### Risks And Edge Cases

- Secondary reads can return `IOError` if the primary deletes SST/blob/WAL files before the secondary has opened or replayed them. The code logs a warning and suggests coordination, custom FS/Env retention, or `max_open_files=-1`, but this only helps table files already held open.
- `TryCatchUpWithPrimary()` treats `IsPathNotFound()` during WAL replay as OK because primary WALs may already be purged, which favors availability but can leave the secondary without unflushed primary writes until they appear in MANIFEST/SST form.
- Secondary iterators do not support explicit snapshots or tailing mode; reads always use latest sequence at call construction time.
- WAL replay ignores missing column families and skips batches covered by existing L0 sequence ranges. These behaviors are necessary for dropped CFs and MANIFEST/WAL overlap, but bugs here would cause duplicate or missing visible writes.
- User-defined timestamp consistency is verified during WAL replay and reads; comparator/CF timestamp-size drift is a high-risk compatibility surface.
- Remote-compaction resumption currently supports only a single subcompaction in progress parsing/persisting and is disabled when output hash verification is enabled. Multi-subcompaction or hash-state resumption would need additional persisted state.
- Progress cleanup can partially delete files before an error returns. The comments explicitly note a partially modified filesystem may require manual cleanup of `secondary_path_`.
- Progress-writer failure paths log that compaction will start without progress persistence, but the helper returns cleanup status to its caller. Tests should pin intended fallback-vs-fail behavior.

### Test Signals

Relevant existing signals include `db_secondary_test.cc` coverage for `OpenAsSecondary`, repeated `TryCatchUpWithPrimary()`, WAL tailing, dropped column families, remote compaction, cancellation, and compaction-progress/resumption behavior. Additional high-value tests should simulate primary file deletion, WAL purge races, timestamp-size changes, blob-backed memtable reads, multi-CF catch-up, invalid progress files with stray SSTs, progress-file rename/sync failures, and resumption disabled by output verification. Static research only; no build or test command was run for this report.
