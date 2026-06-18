# sources/storage-engines/rocksdb/db/db_filesnapshot.cc

## Purpose

`db_filesnapshot.cc` implements DBImpl file-enumeration APIs used by backup, checkpoint, live-file inspection, and WAL discovery paths. It translates current in-memory version state plus filesystem WAL scans into stable lists of live SST, blob, manifest, CURRENT, OPTIONS, and WAL files. Unlike the neighboring test files in this work item, this is production code and sits on a safety boundary: callers use its output to copy or link enough files to reconstruct a consistent DB image.

## Important APIs, Types, and Functions

- `DBImpl::FlushForGetLiveFiles(bool force_atomic_flush)` flushes all column families with `FlushReason::kGetLiveFiles`.
- `DBImpl::GetLiveFiles(std::vector<std::string>&, uint64_t*, bool flush_memtable)` returns relative live table/blob file names plus CURRENT, MANIFEST, and OPTIONS.
- `DBImpl::GetSortedWalFiles()` and `GetSortedWalFilesImpl(VectorWalPtr&, bool need_seqnos)` return sorted WAL metadata, including archived WALs when needed, and cross-check manifest-tracked WALs against directory results.
- `DBImpl::GetCurrentWalFile()` wraps `WalManager::GetLiveWalFile` for the current log number.
- `DBImpl::GetLiveFilesStorageInfo(const LiveFilesStorageInfoOptions&, std::vector<LiveFileStorageInfo>*)` returns richer per-file metadata such as directories, file numbers, types, sizes, checksum info, temperatures, replacement contents, and trim/copy requirements.

## Control Flow

`GetLiveFiles` locks `mutex_`, optionally flushes all column families, walks non-dropped column families through their current versions, appends table and blob filenames, appends CURRENT/MANIFEST/OPTIONS, captures manifest size, and unlocks. It returns names relative to the DB directory.

`GetSortedWalFilesImpl` first disables file deletions when supported, waits for pending obsolete-file purges to finish, snapshots WAL numbers required by the manifest, scans live and archived WAL directories through `wal_manager_`, re-enables deletions, and verifies every manifest-required WAL is included in the sorted scan result.

`GetLiveFilesStorageInfo` begins by deciding whether to flush based on `allow_2pc`, `wal_size_for_flush`, WAL size, and atomic-flush options. While holding `mutex_`, it rejects unsafe blob direct-write cases, flushes if allowed and needed, then records live SST and blob metadata from each non-dropped column family's `VersionStorageInfo`. It captures manifest/options/min-log/current-WAL numbers under the lock, then releases the lock and appends descriptor, CURRENT, and OPTIONS entries. It flushes WAL data, gathers open WAL sizes to identify files that must be copied/truncated rather than hard linked, scans sorted WALs, and appends eligible WAL entries bounded by `min_log_num` and the captured `max_log_num`.

## State and Persistence Behavior

The code observes persisted state from `VersionSet`, `ColumnFamilySet`, `VersionStorageInfo`, `FileMetaData`, blob metadata, WAL manager state, manifest file size, options file size, and current WAL number. It also manipulates operational state by temporarily disabling file deletions and by flushing memtables/WALs to make a snapshot copyable. It deliberately treats CURRENT as replacement contents rather than a normal hard-link candidate because CURRENT can be rewritten. For WALs, `trim_to_size` marks open, recycled, or possibly unsynced logs that must be copied to an exact safe size.

## Dependencies and Integration Points

This file integrates with `DBImpl` mutex and condition variables, `VersionSet`, `ColumnFamilyData`, `VersionStorageInfo`, `WalManager`, `JobContext` deletion state, file naming helpers, checksum constants, blob direct-write state, `LiveFileStorageInfo`, `WalFile`, `FlushWAL`, and checkpoint sync points retained for legacy checkpoint tests.

## Risks and Edge Cases

The main risks are inconsistent snapshots if flush/WAL boundaries are mishandled, file deletion races during WAL scans, omitting manifest-required WALs, hard-linking an unsynced or still-open WAL, and returning partial output after an error. The implementation mitigates these with mutex-held metadata capture, deletion disabling, purge waiting, manifest-vs-directory WAL cross-checks, `max_log_num` bounds, open-WAL size maps, and only moving results to the caller on success. Blob direct writes are a newer edge case: if active blob files cannot be safely flushed because WAL is locked or flushing is disabled, the API returns `NotSupported`.

## Test Signals

Coverage is indirect through checkpoint/backup/live-file tests, WAL tracking tests, blob tests, and sync-point labels named for checkpoint creation. Useful signals are complete live-file lists, absence of deleted-file races, successful checkpoints with WAL copy/link decisions, checksum metadata population, and corruption errors when manifest-required WALs are missing.
