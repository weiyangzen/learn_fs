<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.h -->
# sources/storage-engines/rocksdb/db/builder.h

## Purpose
Declares RocksDB table-building entry points shared by flush, recovery, and compaction-output code. The header exposes the `BuildTable()` contract and small helpers for table builder creation and timestamp metadata extraction.

## Important APIs, Types, And Functions
`TableBuilder* NewTableBuilder(const TableBuilderOptions& tboptions, WritableFileWriter* file)` creates a table builder from the configured table factory. `void ExtractTimestampFromTableProperties(const TableProperties& tp, FileMetaData* meta)` copies timestamp table properties into file metadata. `Status BuildTable(...)` has a wide signature carrying DB name, `VersionSet`, immutable/table/file options, `TableCache`, input iterator, range tombstone iterators, output `FileMetaData`, optional blob additions/garbage, snapshots and snapshot checking, paranoid checks, stats, IO status, IO tracing, blob creation reason, seqno-time mapping, event logging, write lifetime hints, full-history timestamp bounds, blob completion callbacks, current version, payload/garbage counters, flush stats, and fast-SST-open output metadata.

## Control Flow
The header documents the high-level contract: build a table from `iter`, name it by `meta`'s file number, fill the remaining metadata on success, and set `meta->file_size` to zero without producing a table when no data is present. The declaration makes optional outputs explicit by nullable pointers; callers choose which integration lanes, such as blob metadata, table properties, flush stats, or fast-open metadata, they need.

## State And Persistence Behavior
`BuildTable()` mutates `FileMetaData` and optional out-parameters and may create persistent SST/blob files. The header-level contract establishes that zero file size is the sentinel for no produced table. Optional blob vectors are used to communicate manifest-relevant blob additions and garbage to the caller.

## Dependencies And Integration Points
The header includes internal stats, range tombstone fragmentation, seqno-time mapping, table property collectors, version metadata, event logging, column-family options, comparators, env/file APIs, listeners, statuses, table properties, and RocksDB types. Forward declarations keep implementation dependencies lighter while exposing integration with `BlobFileAddition`, `BlobFileGarbage`, `SnapshotChecker`, `TableCache`, `TableBuilder`, `WritableFileWriter`, `BlobFileCompletionCallback`, and `Version`.

## Risks And Edge Cases
The large parameter list is powerful but error-prone: pointer nullability controls behavior, and callers must keep snapshot vectors, timestamp bounds, blob vectors, version pointers, and stats outputs consistent with the table creation reason. Misconfigured options can cause `BuildTable()` to create files with metadata the caller does not record, or skip accounting lanes such as blob garbage. Callers must inspect both returned `Status` and `meta->fd.file_size`.

## Test Signals
Testing is primarily through callers of `BuildTable()` rather than the header. Useful signals include empty-input behavior, metadata population, timestamp property extraction, blob addition/garbage propagation, paranoid file verification, IO error propagation through `IOStatus`, and listener/event-log notifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/builder.h -->
