# sources/storage-engines/rocksdb/examples/compact_files_example.cc

## Purpose
`compact_files_example.cc` demonstrates how external code can implement custom compaction scheduling with RocksDB's `CompactFiles`, `EventListener`, and `GetColumnFamilyMetaData` APIs.

## Important APIs and control flow
The file defines an abstract `Compactor` listener interface with `PickCompaction()` and `ScheduleCompaction()`, a `CompactionTask` struct carrying DB, compactor, column-family name, input files, target level, options, and retry flag, and a `FullCompactor` that compacts all files to the highest level whenever possible.

`FullCompactor::OnFlushCompleted()` picks a task after flush and sets `retry_on_fail` when writes were stopped. `PickCompaction()` gathers all file names from `ColumnFamilyMetaData`, aborting if any file is already being compacted. `ScheduleCompaction()` queues `CompactFiles()` on `options_.env`. The static worker calls `DB::CompactFiles()` and optionally retries non-IO failures.

`main()` disables built-in background compaction, configures small buffers and L0 stall triggers, registers the listener, destroys and opens the DB, writes many keys to force flushes/compactions, verifies values, and closes.

## State, persistence, and integration
Persistent state is the temp DB's SST files and LSM levels. Integration points include flush event callbacks, `Env::Schedule`, compaction metadata, manual compaction options, and DB write/read APIs.

## Risks and test signals
`CompactionTask` stores `const std::string& column_family_name` from callback metadata, which is risky if the referenced string does not outlive scheduled background execution. Retry scheduling does not null-check `new_task` before `ScheduleCompaction(new_task)`. The compactor only calls `GetColumnFamilyMetaData(&cf_meta)` for the default family despite receiving a CF name. Test signals are absence of write stalls with background compaction disabled, correct value reads after many writes, successful scheduled `CompactFiles()` status output, and thread/lifetime sanitizer coverage for listener-scheduled tasks.
