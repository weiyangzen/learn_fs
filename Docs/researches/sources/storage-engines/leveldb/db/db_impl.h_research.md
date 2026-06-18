# sources/storage-engines/leveldb/db/db_impl.h

## Purpose
This header declares `DBImpl`, the concrete implementation of the public `leveldb::DB` interface, and exposes internal test hooks plus option sanitization.

## Important APIs, Types, And Functions
`DBImpl` overrides `Put`, `Delete`, `Write`, `Get`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `GetProperty`, `GetApproximateSizes`, and `CompactRange`. Test-only APIs are `TEST_CompactRange`, `TEST_CompactMemTable`, `TEST_NewInternalIterator`, `TEST_MaxNextLevelOverlappingBytes`, and `RecordReadSample`. Private declarations cover recovery, log replay, memtable flush, write-room management, write grouping, compaction scheduling, compaction output creation/finish/install, and `SanitizeOptions`.

## Control Flow
The header shows the intended lock discipline: most persistent DB state is under `mutex_`, while `table_cache_` has its own synchronization and `shutting_down_`/`has_imm_` are atomics for background coordination. Background work runs through static `BGWork` into instance methods. Manual compaction state is represented by `ManualCompaction`.

## State And Persistence Behavior
Members capture all live DB state: env/options/db name, file lock, current WAL file and writer, `mem_`, immutable memtable, writer queue, snapshots, pending output table numbers, background/manual compaction state, `VersionSet`, background error, and per-level compaction stats. Persistent structures are not encoded here, but the declarations define which objects can mutate logs, manifests, and table files.

## Dependencies And Integration Points
The header depends on internal key format, log writer, snapshots, public DB/Env APIs, port mutex/condvar/thread annotations, and forward declarations for memtable/table-cache/version classes. Tests include this header to downcast `DB*` and call private-ish test hooks.

## Risks And Edge Cases
The main risks are ownership and lifetime: raw pointers for log files, memtables, versions, cache, logger, and DB lock must be released on all paths. Thread annotations document but do not enforce runtime safety. Test hooks bypass public API constraints and can perturb background scheduling.

## Test Signals
Compilation validates interface consistency. Behavioral coverage comes from `db_test.cc`, corruption tests, and fault-injection tests using `DBImpl` hooks to force memtable and range compactions.
