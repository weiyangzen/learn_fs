# sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder.cc

Purpose: implements `SortedRunBuilder`, a utility that ingests unsorted key/value data into a temporary RocksDB instance and emits a compacted sorted run as SST files.

Important APIs and control flow: `SortedRunBuilderImpl::Open()` configures a temporary DB with `VectorRepFactory`, universal compaction, disabled auto-compactions, caller-specified memory/file-size/compression/table/comparator options, WAL disabled for writes, and bulk-load-friendly settings. `Add()` and `AddBatch()` write without WAL and update relaxed entry/data counters. `Finish()` flushes all memtables, forces optimized compaction, collects output file paths and post-compaction metadata stats, and marks the builder finished. `NewIterator()` is allowed only after finish. `Cleanup()`/destructor destroy the temp DB unless `keep_temp_db` is set.

State and persistence: persisted intermediate/output state is the temporary DB directory. Output SST paths are returned after compaction. `finished_`, `cleaned_up_`, relaxed counters, `db_`, and `output_files_` define lifecycle state. WAL is disabled, so resumability is based on flushed SSTs rather than log replay.

Dependencies and integration: uses RocksDB DB, memtable rep, table factory, write batch, filename separator, comparator, and atomic utilities. Public construction is through `SortedRunBuilder::Create()`, which validates options before opening the temp DB.

Risks and test signals: temp directory must not preexist because `error_if_exists = true`. Concurrent `Add()` calls are not explicitly synchronized beyond DB internals; `allow_concurrent_memtable_write` is false. Cleanup uses comparator in `DestroyDB` but not all original options. Finish cannot be called twice, and adding after finish is invalid. A separate `sorted_run_builder_test.cc` exists outside this work item and likely carries functional coverage.
