# sources/storage-engines/foundationdb/fdbserver/workloads/WriteDuringRead.cpp

## Purpose
`WriteDuringRead.cpp` defines the `WriteDuringRead` simulation workload, a self-checking stress test for `ReadYourWritesTransaction` behavior while reads, writes, commits, watches, resets, conflict ranges, and timeouts overlap. It keeps an in-memory model of expected transactional state and compares live FoundationDB reads against that model under many randomized option combinations.

## Important APIs, Types, and Functions
The central type is `WriteDuringReadWorkload : TestWorkload`, registered through `WorkloadFactory<WriteDuringReadWorkload>`. Public workload hooks are `setup`, `start`, `check`, and `getMetrics`. Important helpers include `memoryGetKey`, `memoryGetRange`, and `memoryGet`, which model FDB read semantics over `std::map<Key, Value>`; `getKeyAndCompare`, `getRangeAndCompare`, `getAndCompare`, and `watchAndCompare`, which issue asynchronous reads or watches and verify results; `commitAndUpdateMemory`, which commits and moves the model from pending to committed state; `writeBarrier`, which prevents cancelled write-only transactions from reordering after the next run; and `randomTransaction`, the main randomized operation driver.

## Control Flow
Only client 0 runs the workload. `loadAndRun` repeatedly initializes the database in batches, records `lastCommittedDatabase`, then runs randomized transactions until duration or write-budget limits are reached. `randomTransaction` configures transaction options, seeds a conflict range, schedules a random mix of reads, range reads, key-selector reads, commits, clear operations, atomic operations, watches, delays, resets, and conflict-range additions, then waits for outstanding operations and validates watch outcomes. Errors such as `not_committed`, `commit_unknown_result`, size errors, watch limits, and timeout paths roll the in-memory model back to the last committed state before retrying the outer loop.

## State and Persistence Behavior
Persistent state is ordinary FDB key-value data under a generated prefix, optionally system-key prefixed when `ACCESS_SYSTEM_KEYS` is enabled. The workload keeps volatile mirror state in `memoryDatabase`, `lastCommittedDatabase`, `changeCount`, and `addedConflicts`. Successful commits update the durable store and then assign `lastCommittedDatabase` to the committed in-memory snapshot. Unknown or rejected commits reset volatile state and let the initialization loop reestablish a consistent baseline.

## Dependencies and Integration Points
The file depends on `NativeAPI.actor.h`, `ReadYourWrites`, atomic mutation helpers, `ActorCollection`, `ApiVersion`, and workload tester infrastructure. It exercises FDB transaction options such as `READ_YOUR_WRITES_DISABLE`, `SNAPSHOT_RYW_DISABLE`, `READ_AHEAD_DISABLE`, `PRIORITY_BATCH`, `ACCESS_SYSTEM_KEYS`, `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`, and `TIMEOUT`. In simulation it can target an extra simulated database.

## Risks and Edge Cases
Risk centers on the fidelity of the in-memory model versus real FDB semantics, especially with system keys, byte-limited range reads, key-size truncation for conflict ranges, versionstamped keys, concurrent commit use, and timeout injection. The workload intentionally tolerates `used_during_commit` and cancellation races. A subtle risk is that expected conflict ranges must match the transaction's internal write conflict map exactly when RYW is enabled.

## Test Signals
Failures surface as `TraceEvent(SevError, ...)` records such as `WDRGetWrongResult`, `WDRGetRangeWrongResult`, `WDRGetKeyWrongResult`, `WDRWatchWrongResult`, and conflict range errors. Metrics expose transaction and retry counts. `check` returns the accumulated `success` flag.
