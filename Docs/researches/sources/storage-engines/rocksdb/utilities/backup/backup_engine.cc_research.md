# sources/storage-engines/rocksdb/utilities/backup/backup_engine.cc

## Purpose

This file implements RocksDB's backup and restore engine. It creates point-in-time backups via checkpoint callbacks, stores metadata under a backup directory, shares table/blob files across backups when configured, restores backups into DB/WAL directories, verifies backup contents, deletes old backups, and garbage-collects unreferenced backup files.

## Important APIs, types, and functions

Public entry points are `BackupEngine::Open`, `BackupEngineReadOnly::Open`, `CreateNewBackupWithMetadata`, `PurgeOldBackups`, `DeleteBackup`, `StopBackup`, `GarbageCollect`, `GetBackupInfo`, `GetLatestBackupInfo`, `GetCorruptedBackups`, `RestoreDBFromBackup`, `RestoreDBFromLatestBackup`, and `VerifyBackup`. Internal types include `BackupEngineImpl`, `BackupEngineImplThreadSafe`, `BackupMeta`, `FileInfo`, `WorkItem`, `WorkItemResult`, `BackupAfterCopyOrCreateWorkItem`, `ComputeChecksumWorkItem`, `RestoreAfterCopyOrCreateWorkItem`, and `RemapSharedFileSystem`.

## Control flow

`Initialize` creates or opens the backup directory layout, loads valid metadata files from `meta/`, classifies corrupt backups, computes latest IDs, and starts background worker threads. Backup creation disables DB file deletions, builds a `CheckpointImpl`, schedules copy/create work items for live files and generated files, optionally lets a callback exclude shared checksum files, waits for all work, records metadata, fsyncs directories when requested, and updates latest IDs. Restore resolves excluded files through alternate read-only backup engines, optionally keeps existing DB files by DB session ID or checksum, deletes non-retained files, copies backup files back to DB/WAL directories, and atomically renames `CURRENT.tmp`. Verification checks presence and size and can schedule checksum recomputation. Delete and purge remove metadata first, decrement reference counts, delete unreferenced files, and invoke garbage collection as needed.

## State and persistence behavior

The backup directory uses `private/<backup_id>/`, `meta/<backup_id>`, `shared/`, and `shared_checksum/`. Metadata files are the commit records for backups and are written through temporary meta files followed by rename. `BackupMeta` stores timestamp, approximate sequence number, app metadata, file list, excluded file list, sizes, crc32c hex checksums, and temperatures. In memory, `backuped_file_infos_` reference-counts shared and private files across loaded backups. The engine tracks `latest_backup_id_`, `latest_valid_backup_id_`, corrupt backups, stop state, background threads, and whether another GC might be needed.

## Dependencies and integration points

The implementation integrates with RocksDB `DB`, `CheckpointImpl`, file naming/parsing helpers, `Env` and `FileSystem`, `FSDirectory`, `WritableFileWriter`, `SequentialFileReader`, `LineFileReader`, rate limiters, statistics tickers, table property reading through `SstFileDumper`, DB file checksum metadata, sync points, and public backup options. `RemapSharedFileSystem` lets shared backup files appear inside a private backup directory so backup contents can be opened as a read-only DB for inspection.

## Risks

Backup correctness depends on metadata atomicity, directory fsync behavior, checkpoint file enumeration, and safe sharing names. `share_files_with_checksum=false` is explicitly deprecated because it can lead to data loss. Incremental backups can skip rereading existing shared files, so existing backup corruption is not always detected during new backup creation; `VerifyBackup` is the explicit check path. The background work queue has limited cancellation semantics, and checksum verification waits for scheduled tasks to finish. The code has subtle path handling for shared checksum names, DB session IDs, file sizes, temperatures, excluded files, and restore modes. The read-only facade uses lock ordering across alternate backup engines to avoid TSAN lock inversion reports.

## Test signals

The adjacent `backup_engine_test.cc` covers backup/restore basics, shared checksum naming, restore modes (`kPurgeAllFiles`, `kKeepLatestDbSessionIdFiles`, `kVerifyChecksum`), corruption and schema handling, excluded files, rate limiter clocks, metadata schema options, and option transitions. DB stress code also exercises backup options and schema test hooks.
