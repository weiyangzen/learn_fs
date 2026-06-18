# sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoading.cpp

## Purpose
`BulkLoading.cpp` defines `BulkLoadingWorkload`, a simulation correctness test for low-level bulk load task submission, execution, metadata finalization, and range-lock cleanup. It generates SST files locally, submits bulk-load task states, toggles bulk-load mode, waits for task completion or error, compares loaded data, and ensures KRM metadata is cleared.

## Important APIs, Types, And Functions
Key types are `BulkLoadTaskTestUnit`, `BulkLoading : TestWorkload`, `BulkLoadTaskState`, `BulkLoadFileSet`, `BulkLoadByteSampleSetting`, and `KeyRangeMap<Optional<BulkLoadTaskTestUnit>>`. Important helpers include `clearAllBulkLoadTask`, `submitBulkLoadTask`, `finalizeBulkLoadTask`, `checkAllTaskCompleteOrError`, `checkBulkLoadMetadataCleared`, `generateSSTFiles`, `generateBulkLoadTaskUnit`, `simpleTest`, `complexTest`, and `backgroundWriteTraffic`.

## Control Flow
Only client 0 executes `start`. The workload disables simulation connection failures, optionally initializes all bulk-load task metadata to empty task values, may start background writers, registers the bulk-load range-lock owner, and then randomly selects `simpleTest` or `complexTest`. `simpleTest` submits two non-overlapping tasks over fixed ranges, enables bulk-load mode, waits for completion/error, disables mode to check data, re-enables mode to finalize tasks and acknowledge errors, then waits for metadata cleanup. `complexTest` submits three random possibly overlapping tasks, sometimes waits midstream and toggles mode, tracks outdated subranges in a `KeyRangeMap`, verifies only complete non-error data, finalizes tasks, and checks locks are released.

## State And Persistence
The workload writes generated SST and byte-sample SST files under `simfdb/bulkload/<index>`, bulk-load task metadata under system KRM ranges, range-lock owner records, loaded normal-key data, and optional background traffic. Metadata cleanup is validated by reading `bulkLoadTaskPrefix` over `normalKeys`.

## Dependencies And Integration Points
Dependencies include `fdbclient/BulkLoading.h`, `BulkLoadUtil`, `RocksDBCheckpointUtils`, `StorageMetrics`, range locks, DD bulk-load mode, RocksDB SST writers, byte-sampling helpers, and tester/simulator infrastructure. The file directly exercises server-side bulk-load task state transitions without going through a dump job.

## Risks
The generated file set initially uses an empty manifest name and relies on simulation assumptions. Background traffic futures are created in a local vector and not awaited, so they exist only as fire-and-forget actors during the test scope. Overlapping ranges deliberately create outdated task fragments; correctness depends on ignoring outdated and error ranges consistently. `checkBulkLoadMetadataCleared` has special expectations when metadata was preinitialized. Range-lock leaks would affect later workloads, so owner removal and `findExclusiveReadLockOnRange` assertions are important.

## Test Signals
Trace signals include `BulkLoadingSubmitBulkLoadTask`, `BulkLoadingWorkLoadIncompleteTasks`, `BulkLoadingWorkLoadFailedTasks`, `BulkLoadingDataProduced`, `BulkLoadingWorkLoadDataWrong`, `BulkLoadingWorkLoadSimpleTestComplete`, and `BulkLoadingWorkLoadComplexTestComplete`. Primary pass/fail signals are `ASSERT`s for data equality, metadata cleanup, task phases, and empty range locks.
