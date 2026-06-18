# sources/storage-engines/rocksdb/db/obsolete_files_test.cc

## Purpose
`obsolete_files_test.cc` validates RocksDB obsolete-file discovery and purge behavior for WALs, options files, SST/blob files, direct-write blobs, and no-op purge synchronization. It focuses on safety: obsolete files should be deleted, live or ambiguous files should be kept, and purge bookkeeping should not race with DB close or WAL listing.

## Important APIs, Types, And Functions
Helpers include `WriteFooterlessBlobFile`, which writes a blob log header and record without a footer, and `ListBlobFileNumbers`, which parses `.blob` children in a directory.

`ObsoleteFilesTest` extends `DBTestBase` and defines `AddKeys`, `createLevel0Files`, `CheckFileTypeCounts`, and `ReopenDB`. `ReopenDB` configures low L0 compaction trigger, full obsolete-file purge (`delete_obsolete_files_period_micros = 0`), WAL TTL/size, a separate WAL directory, and disabled stats dumping to avoid unrelated races.

The tests use `DBImpl::FindObsoleteFiles`, `PurgeObsoleteFiles`, `DisableFileDeletions`, `EnableFileDeletions`, `SetOptions`, blob metadata APIs, `JobContext`, sync points, `GetSortedWalFiles`, and test mutex/purge wait hooks.

## Control Flow
`RaceForObsoleteFileDeletion` forces a background compaction to find obsolete files, then starts a user thread that also calls `FindObsoleteFiles` and `PurgeObsoleteFiles` under controlled sync points. It asserts deletion statuses are OK and close-helper pending purge state is empty.

`DeleteObsoleteOptionsFile` disables file deletions while toggling options several times, re-enables deletions, closes the DB, and verifies only two current options files remain.

`BlobFiles` manually adds one obsolete blob file to `VersionSet` and one live blob file to current `VersionStorageInfo`, runs `FindObsoleteFiles`, checks delete/live lists and `files_grabbed_for_purge`, then adds full-scan candidates and verifies purge deletes only old and obsolete blobs while retaining live and pending blobs.

`FooterlessBlobFileIsKeptDuringPurge` creates a blob file without a footer, makes it a full-scan candidate, and verifies purge does not delete it. `SealedDirectWriteBlobFileIsKeptDuringPurge` enables direct blob writes, writes two large values, identifies a sealed blob file, schedules purge, waits for purge completion, verifies the key still reads, and checks the file was not deleted.

`GetSortedWalFilesHangsAfterNoopPurge` reproduces a previous hang: an iterator destruction triggers a purge path with no files to delete while another thread waits in `GetSortedWalFiles`. Sync points force the wait ordering and joining the thread proves the condition variable was signaled.

## State And Persistence Behavior
The suite manipulates real DB directories, WAL directories, manifests, options files, SSTs, and blob files. It verifies both in-memory purge bookkeeping (`JobContext`, `files_grabbed_for_purge`, live blob metadata) and file-system-visible results.

Blob purge safety is conservative. Files listed as live, pending output, pending minimum blob number, footerless/possibly incomplete, or direct-write sealed and still referenced must remain on disk. Only files known obsolete or old full-scan candidates below pending thresholds are deleted.

Options-file persistence is tested by repeated option changes while deletion is disabled. On close/re-enable, obsolete options files should be cleaned so only the latest bounded set remains.

## Dependencies And Integration Points
The file depends on DB internals (`DBImpl`, `VersionSet`, `VersionStorageInfo`, `JobContext`), blob log writer/metadata, filename parsing, file read/write helpers, SyncPoint, and DBTestBase.

Integration points include compaction-generated obsolete files, WAL TTL/size cleanup, manifest/live metadata, delayed file deletion, scheduled purge workers, DB close cleanup, direct blob write partitioning, and `DB::GetSortedWalFiles`.

## Risks
File deletion is race-prone. The same file can be discovered by background compaction, a forced user scan, or close cleanup; the grabbed-for-purge set must prevent double deletion and must be cleared after purge.

Blob files have several ambiguous states. Footerless files may be incomplete and should not be purged merely because they appear old. Direct-write blobs can be sealed yet still required by unflushed or visible keys. No-op purge paths must notify waiters even without deleting files.

Assertions depend on file-name parsing and exact file-type counts. Changes in options-file retention policy or blob naming would require test updates while preserving safety invariants.

## Test Signals
Success signals include OK delete statuses, exact WAL/options file counts, `JobContext` delete/live blob lists, expected blob filenames in deletion callbacks, retained footerless/direct-write blob files, successful reads after scheduled purge, empty pending-purge sets on close, and `GetSortedWalFiles` returning without hanging.
