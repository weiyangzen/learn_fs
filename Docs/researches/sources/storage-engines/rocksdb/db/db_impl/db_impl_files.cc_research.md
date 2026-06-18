# sources/storage-engines/rocksdb/db/db_impl/db_impl_files.cc

## Purpose

`db_impl_files.cc` owns DBImpl file lifecycle decisions: determining which WAL, SST, blob, manifest, OPTIONS, info-log, temp, and identity files are live; suppressing or re-enabling deletion; purging obsolete files; computing minimum WAL retention for recovery; maintaining DB identity; and updating the next file number after recovery. It is a central persistence-safety component because it decides when durable artifacts can be deleted, recycled, archived, or retained.

## Important APIs, Types, And Functions

- `DBImpl::DisableFileDeletions`, `DisableFileDeletionsWithLock`, `EnableFileDeletions`, and `IsFileDeletionsEnabled` implement the public deletion gate via `disable_delete_obsolete_files_`.
- `DBImpl::FindObsoleteFiles(JobContext*, bool force, bool no_full_scan)` fills a `JobContext` with live file numbers, delete candidates, WAL state, manifest state, pending outputs, protected blob files, quarantined files, and optional full directory scan candidates.
- `DBImpl::PurgeObsoleteFiles(JobContext&, bool schedule_only)` converts the `JobContext` into concrete delete/archive/recycle/cache-release actions without holding the DB mutex for the slow path.
- `DBImpl::DeleteObsoleteFileImpl` performs actual file deletion and emits table/blob deletion events.
- `DBImpl::DeleteObsoleteFiles` is the mutex-held full-scan entry point used after open and in other cleanup paths.
- `DBImpl::ShouldKeepBlobFileDuringPurge` and the file-local `ShouldKeepFooterlessBlobFile` protect blob files that are tracked, active for direct write, or not yet footer-complete.
- `GetDBRecoveryEditForObsoletingMemTables`, `PrecomputeMinLogNumberToKeepNon2PC`, `PrecomputeMinLogNumberToKeep2PC`, and `FindMinPrepLogReferencedByMemTable` compute WAL retention edits after flush or mempurge, including two-phase-commit prepared-section retention.
- `DBImpl::SetupDBId` and `SetDBId` reconcile DB identity between MANIFEST and `IDENTITY`.
- `DBImpl::CollectAllDBPaths` and `MaybeUpdateNextFileNumber` discover DB/CF paths and ensure recovered file-number allocation cannot collide with on-disk files.

## Control Flow

Deletion control starts with `FindObsoleteFiles`. Under `mutex_`, it exits early if deletion is disabled, decides whether to perform a full filesystem scan based on `force`, `no_full_scan`, and `delete_obsolete_files_period_micros`, snapshots retention state into the `JobContext`, gathers obsolete files from `VersionSet`, marks files grabbed for purge, records manifest/log thresholds, and either collects all candidate files from DB/WAL/log directories or removes still-live files from the version-provided delete lists. It then increments `pending_purge_obsolete_files_` before crossing into WAL cleanup so readers of sorted WALs can wait for purge completion.

WAL cleanup in `FindObsoleteFiles` coordinates `mutex_`, `wal_write_mutex_`, `wal_sync_cv_`, `alive_wal_files_`, `logs_`, `wal_recycle_files_`, and `wals_to_free_`. WALs older than `MinLogNumberToKeep()` are either moved to the recycle list or scheduled for deletion, their sizes are removed from `wals_total_size_`, and old log writers are detached after waiting for in-flight syncs. The DB mutex can be temporarily released while closing inactive WAL files, then reacquired before returning.

`PurgeObsoleteFiles` runs the slower side. It builds live/recycle/quarantine sets, expands explicit SST/blob/WAL/manifest delete lists into candidate file names, releases table-cache handles for obsolete SSTs, deduplicates candidates, keeps the newest two OPTIONS files adjusted by `min_options_file_number`, closes detached WAL writers, and then evaluates each candidate by `FileType`. WALs are kept if above the min log, equal to prev log, or marked for recycling; manifests are kept if current or newer; table files are kept if live or pending; blob files are kept if live, pending, protected, newer than next file, or footerless/tracked; temp/options/current/lock/identity/meta files have their own keep rules. Files not owned by this DB instance are skipped. WALs can be archived rather than deleted when TTL or size limit is configured. Deletions can be immediate or scheduled through pending purge.

The WAL-retention helpers compute manifest edits for recovery cleanup. Non-2PC mode combines the flushed CF's new log number with other CFs' unflushed-data minimum. 2PC mode additionally considers outstanding prepared transactions in `LogsWithPrepTracker` and prepared sections still referenced by live or immutable memtables.

DB identity setup first tries to read `IDENTITY` for existing DBs and compare it with any MANIFEST DB ID. If missing or invalid, it generates a unique ID when needed and writes `IDENTITY` unless read-only or `write_identity_file` disables it. `MaybeUpdateNextFileNumber` scans every DB and CF path, records existing table/blob files into the recovery context, advances `next_file_number_` above any on-disk number, and emits a recovery edit unless the recovery-manifest optimization can skip a noop.

## State And Persistence Behavior

Persistent artifacts are protected by several independent retention gates: `pending_outputs_` for files being produced, `min_options_file_numbers_` for remotely referenced OPTIONS files, `VersionSet` live file sets, active/protected blob direct-write file numbers, WAL log numbers, manifest numbers, WAL tracking state, WAL recycling state, and quarantine from the error handler. `pending_purge_obsolete_files_` is the coordination bridge between discovery and actual purge. File deletion affects table cache, blob/table deletion listeners, WAL manager archive state, delete scheduler state, info-log retention, and optional WAL recycling.

`SetupDBId` persists or validates DB identity, while `MaybeUpdateNextFileNumber` persists file-number allocator advancement through `RecoveryContext::UpdateVersionEdits`. The file also records existing data files so higher-level open code can track them with the SST file manager.

## Dependencies And Integration Points

This file integrates with `VersionSet`, `ColumnFamilyData`, `MemTableList`, `LogsWithPrepTracker`, `JobContext`, `TableCache`, `BlobFilePartitionManager`, `WalManager`, `DeleteScheduler`, `SstFileManagerImpl`, `EventHelpers`, `FileSystem`/`Env`, and filename parsing helpers. It is called by open/recovery, flush/compaction cleanup, manual file-deletion APIs, WAL recovery, follower catch-up cleanup, and error-handling quarantine flows.

## Risks And Edge Cases

- Incorrect candidate classification can delete live SST/blob/WAL files or leak obsolete files indefinitely.
- Full scans race with in-progress direct-write blob files; the footerless-blob check is intentionally conservative.
- WAL cleanup has lock-order and sync-wait complexity. Regressions can deadlock writers or free a log writer while it is syncing.
- Secondary/follower ownership must be respected through `OwnTablesAndLogs`; otherwise one DB instance can delete another instance's files.
- `MaybeUpdateNextFileNumber` must handle crash-created files at exactly the previous next number to avoid allocator collision.
- 2PC WAL retention must account for outstanding prepared transactions and memtables with prepared sections; missing one can break recovery.
- Delete scheduling versus immediate deletion affects durability ordering, directory fsync, rate limiting, and test determinism.

## Test Signals

Useful test coverage includes deletion-disable nesting, full-scan and no-full-scan obsolete cleanup, WAL recycle and archive behavior, pending-output protection, blob direct-write/footerless retention, DB identity mismatch/missing-file recovery, best-efforts recovery file-number advancement, 2PC prepared WAL retention, secondary/follower file ownership, and crash/restart tests with created but unmanifested SST/blob/WAL files. The file has many `TEST_SYNC_POINT` hooks around deletion, WAL closing, blob retention, and recovery edit emission that are intended for race and fault-injection tests.
