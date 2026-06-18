# sources/storage-engines/rocksdb/include/rocksdb/utilities/sorted_run_builder.h

## Purpose
Utility interface for using a temporary RocksDB instance as an external sorter that emits sorted SST files for ingestion.

## Important APIs, Types, And Functions
`SortedRunBuilderOptions` configures temp directory, comparator, SST size, compression, compaction threads, memory, write-buffer count, table factory, and temp retention. `SortedRunBuilder` exposes `Create`, `Add`, `AddBatch`, `Finish`, `GetOutputFiles`, `GetNumEntries`, `GetDataSize`, `NewIterator`, and `Cleanup`.

## Control Flow, State, And Persistence
Callers add records or batches, call `Finish()` to flush/compact into seqno-zero sorted SSTs, then retrieve files or iterate output. Temporary DB files live under `temp_dir`; cleanup is automatic unless `keep_temp_db` is true.

## Dependencies And Integration Points
Depends on `Options`, `Comparator`, `Iterator`, `WriteBatch`, `TableFactory`, `Slice`, and `Status`. Integrates with `IngestExternalFile` bulk-loading workflows.

## Risks And Edge Cases
`temp_dir` is required. `Add`/`AddBatch` are thread-safe but other methods are not concurrent-safe. Counts and sizes are approximate before finish. Duplicate keys may overcount before final compaction. Ingestion requires specific options.

## Test Signals
Cover empty/non-empty runs, duplicate resolution, concurrent adds, batch ingestion, custom comparators, finish output validity, iterators, cleanup behavior, and ingestion into a target DB.
