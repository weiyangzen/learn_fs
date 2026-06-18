<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.cc -->
# sources/storage-engines/rocksdb/db/builder.cc

## Purpose
Implements RocksDB table creation for flush/recovery/compaction-style paths. `BuildTable()` consumes an internal iterator plus range tombstones, optionally creates blob files, writes an SST through a `TableBuilder`, fills `FileMetaData`, performs verification and IO finalization, tracks blob garbage/additions, emits listener/event-log notifications, and cleans up failed or empty outputs.

## Important APIs, Types, And Functions
`NewTableBuilder()` delegates to the configured table factory after asserting column-family ID/name consistency. `ExtractTimestampFromTableProperties()` copies `rocksdb.timestamp_min` and `rocksdb.timestamp_max` user properties into `FileMetaData`. `BuildTable()` is the central function; important collaborators include `OutputValidator`, `CompactionRangeDelAggregator`, `BlobGarbageMeter`, `BlobCountingIterator`, `MergeHelper`, `BlobFileBuilder`, `CompactionIterator`, `WritableFileWriter`, `TableCache`, `SeqnoToTimeMapping`, `EventHelpers`, and `TableProperties`.

## Control Flow
`BuildTable()` initializes metadata, optionally wraps the input iterator with `BlobCountingIterator` for flush-time blob garbage accounting, seeks input, aggregates fragmented range tombstones, builds the output table file name, and notifies listeners that table creation started. If there are point records or range tombstones, it may create a compaction filter for table-file creation, opens a writable SST with a no-reopen/no-readers contract, wraps it in `WritableFileWriter`, creates a `TableBuilder`, and constructs a `CompactionIterator`. When blob files are enabled and level/options allow it, `BlobFileBuilder` is attached so eligible values are emitted to blob files while table values become blob references.

During iteration, each compaction output key/value is optionally rewritten from `kTypeValuePreferredSeqno` to a packed preferred seqno or plain `kTypeValue`, added to the output validator and table builder, counted in flush stats, passed through blob garbage outflow accounting, and used to update `FileMetaData` boundaries. Range tombstones are serialized after point keys and update range boundaries and compensated range-deletion size. The builder is abandoned on error or empty output; otherwise relevant seqno-time mappings are copied, table properties are set, and `Finish()` completes the table.

After finish, the function propagates builder IO status, fills file size/tail/checksum/unique ID/table properties/timestamp fields, syncs and closes the writer, finishes or abandons attached blob file creation, opens the new table through `TableCache` for usability checks, optionally performs paranoid output hash validation by scanning the file, checks iterator status, emits blob garbage records, and deletes SST/blob files on failure or empty output. Final events use `(nil)` and an aborted listener status for empty SSTs even when the returned status is OK.

## State And Persistence Behavior
Successful execution persists an SST file, optional blob files, file checksums, unique IDs, table properties, timestamp ranges, smallest/largest keys and sequence numbers, blob additions, blob garbage, memtable payload/garbage byte estimates, flush stats, and optional fast-open metadata. Failed or empty builds delete the partially created SST and any created blob files and release obsolete table-cache handles. The function is careful to sync/close before exposing checksum metadata and to notify listeners both at start and finish.

## Dependencies And Integration Points
This file is a core integration point among DB options, file systems, table factories, compaction iteration, merge operators, compaction filters, range tombstone aggregation, blob file generation, table cache verification, IO tracing, listeners, event logging, internal stats, thread-status IO reporting, sequence-number-to-time mapping, and version metadata. `BuildTable()` is declared in `db/builder.h` and is called by flush/recovery paths and related table-materialization code. It also cooperates with `Version`/`ColumnFamilyData` for blob fetching during flush/recovery and range-deletion size approximation.

## Risks And Edge Cases
The function must correctly handle empty input with only tombstones, builder errors that leave `s` OK, iterator errors after output work, IO status vs logical status precedence, blob builder abandonment after table failure, and cleanup of files that were created but must not enter the version set. Preferred-seqno rewriting depends on `SeqnoToTimeMapping` and must preserve metadata bounds. Flush-time filters must have `IgnoreSnapshots() == true`; otherwise table creation is rejected. Blob garbage accounting is only enabled when the caller supplies `blob_file_garbages`, and correctness depends on tracking both input and surviving output blob references.

## Test Signals
Direct test hooks include sync points such as `BuildTable:create_file`, `BuildTable:BeforeFinishBuildTable`, `BuildTable:BeforeCheckEmpty`, `BuildTable:BeforeSyncTable`, `BuildTable:BeforeCloseTableFile`, `BuildTable:BeforeOutputValidation`, and `BuildTable:BeforeDeleteFile`. Broader coverage comes from RocksDB flush, recovery, compaction, table-cache, blob, range-deletion, checksum, timestamp, and fault-injection tests. The blob direct-write and blob-index suites in this subset exercise related blob metadata, filter, garbage, and readback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.cc -->
