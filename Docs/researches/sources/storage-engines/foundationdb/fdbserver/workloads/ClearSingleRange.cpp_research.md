# sources/storage-engines/foundationdb/fdbserver/workloads/ClearSingleRange.cpp

## Purpose
`ClearSingleRange.cpp` defines the `ClearSingleRange` tester workload. It waits for a configured delay, then clears one configured key range in a single transaction.

## Important APIs, Types, And Functions
The file defines `ClearSingleRange : TestWorkload` and registers it with `WorkloadFactory<ClearSingleRange>`. The central actor is `fdbClientClearRange(Database db)`, which uses `Transaction`, `FDBTransactionOptions::NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`, `tr.clear(KeyRangeRef(begin, end))`, `tr.commit`, and `tr.onError`.

## Control Flow
The constructor reads `begin`, `end`, and `beginClearRange` options, defaulting to `normalKeys`. Only client 0 runs `start`. The actor logs the target range, sets the next-write-no-conflict-range option, waits `startDelay`, clears the range, and commits.

## State And Persistence
The persistent effect is removal of all keys in `[begin, end)`. The transaction option prevents adding a write conflict range for the clear, which changes conflict behavior compared with a normal range clear. There is no workload-local persistence.

## Dependencies And Integration Points
The workload depends on native API transactions and tester workload registration. It includes `BulkSetup.h` but does not use any symbols from it. It can be combined with other workloads to test behavior under asynchronous range deletion.

## Risks
The retry logic is incomplete: after catching an error, the actor logs `ClearRangeError` and calls `tr.onError(err)` once, but does not loop back to reissue the clear. If the commit fails transiently, the workload may end without clearing the range. It also logs an error object even when no error was caught, which may be noisy or invalid depending on `Error` default semantics.

## Test Signals
Signals are `ClearSingleRange` and `ClearRangeError` traces. `check` always returns true, so verifying the range was actually cleared requires another workload or direct key inspection.
