# sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.cc

## Purpose

`compacted_db_impl.cc` implements `CompactedDBImpl`, a read-only DB implementation optimized for fully compacted databases with a very simple file layout. It bypasses normal DBImpl read paths and directly chooses an SST file by key range before calling the table reader. The mode is intentionally narrow: it supports reads from the default column family when all data is in one sorted level or in a single L0 file, and rejects layouts needing normal LSM merging.

## Important APIs, Types, and Functions

- The constructor calls the `DBImpl` read-only base constructor and initializes cached column-family/version/comparator pointers.
- `FindFile(const Slice& key)` binary-searches the `LevelFilesBrief` array by largest user key.
- `Get(...)` validates `ReadOptions::io_activity`, timestamp compatibility, builds a `LookupKey` at `kMaxSequenceNumber`, chooses a file, opens/pins it through `TableCache::FindTable`, and calls `TableReader::Get`.
- `MultiGet(...)` performs the same logic per key, but is explicitly not optimized like `DBImpl::MultiGet`.
- `Init(const Options&)` recovers the default CF read-only, installs a super version, validates the compacted layout, and caches `cfd_`, `version_`, `user_comparator_`, `files_`, and `files_level_`.
- `Open(...)` validates `max_open_files=-1` and no merge operator, constructs the DB, initializes it, marks it opened, optionally schedules async file opening, starts periodic tasks, and returns the DB pointer.

## Control Flow

On open, `Init` calls `Recover` in read-only mode for the default CF, installs a super version, and examines `VersionStorageInfo`. It rejects empty DBs, more than one L0 file, a mixture of L0 and other levels, or multiple non-empty non-L0 levels. If exactly one L0 file exists, reads use L0. Otherwise the last non-empty sorted level becomes the file array.

On `Get`, the implementation normalizes IO activity to `kGet`, enforces timestamp read rules, clears an optional returned timestamp, creates `GetContext` and `BlobFetcher`, finds the candidate file, checks the key is not below that file's smallest key, opens the table with index/filter prefetch and pinned table handle, and calls `TableReader::Get`. It maps found/not-found context state to `Status::OK` or `Status::NotFound`.

`MultiGet` validates IO activity and timestamp options once, initializes all statuses on validation failure, clears returned timestamps, then loops over keys with the same file selection and direct table-reader lookup used by `Get`.

## State and Persistence Behavior

The implementation does not write persistent state. It reads recovered MANIFEST/version state and caches pointers into the default column family's current super version. All mutating operations are disabled in the header. Blob values are fetched through `BlobFetcher` using the cached version. Timestamp handling uses current CF metadata and can reject reads against collapsed history.

## Dependencies and Integration Points

This file integrates `DBImpl` recovery/open lifecycle, `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `LevelFilesBrief`, `TableCache`, `TableReader`, `GetContext`, `LookupKey`, timestamp validation helpers, `BlobFetcher`, and DB logging/periodic-task startup. It depends on sorted non-overlapping file ranges when using a non-L0 level.

## Risks and Edge Cases

`FindFile` assumes `files_.num_files > 0` and sorted file ranges; incorrect layout validation would make direct lookup unsafe. The binary search passes `files_.files + right`, which excludes the last slot as the upper bound expression relies on `right = num_files - 1`; this makes layout assumptions worth test attention around first/last files. The implementation supports only default CF and no merge operator, so callers expecting full DB semantics must use normal read-only DB modes. Timestamp and blob behavior add risk because this optimized path must preserve normal read semantics while bypassing DBImpl's richer read machinery.

## Test Signals

Expected test signals are successful `DB::OpenForReadOnly`/compacted-mode opens for fully compacted layouts, `InvalidArgument` for unsupported options, `NotSupported` for unsupported layouts, point-read parity with normal DB reads, blob-value reads, timestamp mismatch/collapsed-history errors, and failed write/flush/compaction calls.
