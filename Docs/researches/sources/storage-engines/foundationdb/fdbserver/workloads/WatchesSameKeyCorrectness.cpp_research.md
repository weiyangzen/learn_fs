# sources/storage-engines/foundationdb/fdbserver/workloads/WatchesSameKeyCorrectness.cpp

## Purpose
`WatchesSameKeyWorkload` validates subtle same-key watch behavior, including multiple watches on one key, ABA value changes, and same-version/different-value commits.

## Important APIs, Types, and Functions
The workload uses `ReadYourWritesTransaction`, `Transaction::watch()`, `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`, deterministic random values, and helpers `setKeyRandomValue()` and `watchKey()`. It runs five case actors during setup.

## Control Flow
`setup()` starts `case1` through `case5` on distinct keys. `start()` waits for all cases. Case 1 creates multiple watches in the same transaction and triggers all with a later write. Case 2 creates an earlier watch, then multiple later watches, verifying all fire. Case 3 creates an ABA scenario where one watch is canceled and no refire is required. Case 4 creates ABA with multiple futures and verifies a new write fires both. Case 5 uses no-write-conflict writes in two transactions to exercise same-version different-value watch behavior, waits for at least one watch, writes a new value, and waits for both.

## State and Persistence Behavior
Database state is five test keys `foo1` through `foo5` with changing random values. Watch futures are transient local state. The workload does not clean keys after completion.

## Dependencies and Integration Points
It integrates with RYW transactions, Native API watches, storage-server watch response logic described in comments, conflict range options, and tester workload registration.

## Risks and Edge Cases
The same-version behavior in case 5 says commits "hopefully" share a version due to disabled write conflict ranges; if scheduling changes, the exact path may vary. Cases use long retry loops and can hang if watches fail to fire. `check()` only inspects future errors after `waitForAll()` returns.

## Test Signals
Successful completion of all case futures is the primary signal. `check()` returns false if any case future errored. Assertions are implicit through awaited watch futures and transaction error handling.
