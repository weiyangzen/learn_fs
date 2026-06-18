# sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.h

## Purpose

`db_stress_listener.h` declares `UniqueIdVerifier` and defines almost all `DbStressListener` event callbacks inline. The listener validates event metadata, injects timing perturbations, toggles fault injection around background work, tracks compaction callback ordering, records persisted flush sequence numbers, verifies table-file paths, and checks SST unique IDs.

## Important APIs, Types, and Functions

- `DbStressListener : public EventListener` overrides flush, compaction, subcompaction, table creation/deletion, ingestion, file IO, background error/stall/pressure, shutdown, and error-recovery callbacks.
- `VerifyFileDir()`, `VerifyFileName()`, and `VerifyFilePath()` assert table-file path validity in debug builds.
- `RandomSleep()` sleeps up to 5 ms to expose callback lock/timing bugs.
- `FileNumberFromPath()` extracts SST file numbers for compaction tracking.
- Internal state includes `num_pending_file_creations_`, `unique_ids_`, `shared_`, `db_fault_injection_fs_`, `compacting_files_`, `precommitted_jobs_`, and `shutting_down_`.

## Control Flow and State Behavior

`OnFlushBegin()` enables thread-local read/write/metadata fault injection when available. `OnFlushCompleted()` validates metadata, sleeps, disables injection, and updates `SharedState` persisted sequence number.

Compaction callbacks enforce ordering. `OnCompactionBegin()` inserts input file numbers into `compacting_files_`. `OnCompactionPreCommit()` removes them and records the job by id. `OnCompactionCompleted()` validates paths and asserts a matching PreCommit record. `OnTableFileDeleted()` aborts if a table is deleted while still tracked as compacting, except during shutdown.

Table creation callbacks count pending creations, validate successful outputs, verify table properties, and run unique-ID checks. External ingestion verifies the ingested table's unique ID. Error recovery can temporarily disable fault injection and exclude flush IO.

## Dependencies and Integration Points

The header depends on RocksDB listener APIs, table properties and unique-ID APIs, filename parsing, `SharedState`, remote compaction service constants, fault-injection filesystem utilities, gflags declarations, atomic wrappers, and random utilities. It is installed from `db_stress_test_base.cc`, while `db_stress_listener.cc` implements construction and unique-ID persistence.

## Risks and Edge Cases

The listener intentionally asserts inside RocksDB callbacks, giving strong signal but terminating long runs on false positives. Shutdown is special because compaction callbacks may be skipped, so deletion checks are suppressed after shutdown begins. Compaction tracking assumes job ids are unique while precommitted jobs await completion and that input file info matches between callbacks.

`num_pending_file_creations_` must return to zero before destruction. Debug-only path validation disappears under `NDEBUG`. Fault-injection pairing bugs could leave injection enabled or disabled for the wrong scope.

## Test Signals

Useful signals include no file-path assertions, no duplicate SST unique IDs, no concurrent compaction of the same input file, every completed compaction having a prior PreCommit, no deletion while an SST is between Begin and PreCommit, and clean listener destruction with zero pending table creations.
