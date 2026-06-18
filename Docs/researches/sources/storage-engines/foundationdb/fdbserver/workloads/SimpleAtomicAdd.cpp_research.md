# sources/storage-engines/foundationdb/fdbserver/workloads/SimpleAtomicAdd.cpp

## Purpose
`SimpleAtomicAddWorkload` verifies basic `MutationRef::AddValue` behavior by applying a fixed number of atomic adds to one key and checking the final integer value.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SimpleAtomicAdd`. Important options are `addValue`, `iterations`, `initialize`, `initialValue`, `sumKey`, and `testDuration`. Core actors are `setInitialValue`, `applyAtomicAdd`, and `_check`.

## Control Flow
Only client 0 runs. `_start` optionally initializes `sumKey`, pushes `iterations` timeout-wrapped `applyAtomicAdd` futures, and calls `waitForAll(clients)`. Each add actor uses a `ReadYourWritesTransaction`, calls `atomicOp(sumKey, val, MutationRef::AddValue)`, and retries on errors. `_check` reads the key and compares it to `addValue * iterations + initialValue`.

## State And Persistence Behavior
The workload persists a little-endian integer byte representation at `sumKey`. Atomic adds are committed independently and concurrently. The check copies the stored bytes into a `uint64_t`, defaulting to zero when absent.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWritesTransaction`, generic actor timeout helpers, and FoundationDB atomic mutation semantics. It is a narrow sanity workload for atomic addition.

## Risks And Edge Cases
The `_start` actor calls `waitForAll(clients)` without `co_await` or returning it, which means the start actor can finish before client futures complete. Timeouts still wrap individual add actors, but lifecycle expectations depend on actor retention in the `clients` vector and later `check`. Integer width and signedness are also notable: `addValue` is an `int`, while expected and actual are compared as `uint64_t`.

## Test Signals
Trace events `SAABegin`, `SAASetInitialValue`, and `SAACheckEqual` show operations and final comparison. `_check` returns false on mismatch; setup/add/check retry errors emit corresponding `SAA*Error` traces.
