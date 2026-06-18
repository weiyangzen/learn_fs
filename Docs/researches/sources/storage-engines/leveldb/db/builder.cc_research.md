<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.cc -->
# sources/storage-engines/leveldb/db/builder.cc

## Purpose
Implements `BuildTable()`, the compaction/flush helper that writes an iterator stream into one sorted table file and fills `FileMetaData`.

## Important APIs, Types, And Functions
Function `Status BuildTable(const std::string& dbname, Env* env, const Options& options, TableCache* table_cache, Iterator* iter, FileMetaData* meta)`.

## Control Flow
Initializes `meta->file_size` to zero, seeks iterator to first, creates `TableFileName(dbname, meta->number)` only when data exists, writes all key/value pairs through `TableBuilder`, records smallest/largest internal keys, finishes/syncs/closes file, verifies by opening through `TableCache`, checks iterator status, and removes the file on any failure or empty input.

## State And Persistence Behavior
Creates, syncs, closes, verifies, and possibly deletes an `.ldb` table file. Mutates `FileMetaData` fields `file_size`, `smallest`, and `largest`.

## Dependencies And Integration Points
Depends on internal `dbformat`, `filename`, `table_cache`, `version_edit`, public `Env`, `Iterator`, and `TableBuilder` via LevelDB DB includes. Called by DB implementation compaction/flush paths to materialize SSTables and feed metadata into version edits.

## Risks
Input iterator keys must be ordered and encoded as internal keys; file cleanup depends on `Env::RemoveFile`; verification only checks iterator status from table cache, not a full scan.

## Test Signals
Covered indirectly by DB, recovery, corruption, table, compaction, and builder-driven flush/compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/builder.cc -->
