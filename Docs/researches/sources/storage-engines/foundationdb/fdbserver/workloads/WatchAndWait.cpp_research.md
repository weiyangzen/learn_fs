# sources/storage-engines/foundationdb/fdbserver/workloads/WatchAndWait.cpp

## Purpose
`WatchAndWaitWorkload` creates many watches and waits for them to trigger, measuring trigger rate. It is a watch scaling and lifecycle workload.

## Important APIs, Types, and Functions
The workload uses `ReadYourWritesTransaction::watch()`, `maxOutstandingWatches`, generated fixed-width keys, `PerfIntCounter`, and `PerfMetric`. Key methods are `keyForIndex()` and `watchAndWait()`.

## Control Flow
`start()` divides the node range across clients, calculates `NodesPerWatch = nodeCount / watchCount`, launches a watch actor for each assigned index, waits for `testDuration`, and exits. Each `watchAndWait()` actor repeatedly sets `cx->maxOutstandingWatches` high, watches one key, commits the watch transaction, waits for the watch to fire, increments trigger count, then calls `tr.onError(err)` after any caught error and increments retries.

## State and Persistence Behavior
The workload itself does not write watched keys; it relies on other workloads or configuration to trigger watches. It maintains counters for triggers and retries. Key shape optionally includes a node prefix and can use separate keys when `triggerWatches` is false.

## Dependencies and Integration Points
It integrates with the Native API watch implementation, tester key generation, other workloads that mutate watched keys, and client watch limits.

## Risks and Edge Cases
If `watchCount` is zero or larger than adjusted `nodeCount`, division or launch behavior can be problematic; the constructor caps only the greater-than case. `watchAndWait()` calls `onError()` even after successful watch completion with an uninitialized/default error path in the loop structure, which is unusual. `check()` always returns true.

## Test Signals
Metrics include triggers/sec, total triggers, and retries. Traces include `WatchAndWaitExpect`, `WatchAndWaitEnd`, and `WatchAndWaitError`.
