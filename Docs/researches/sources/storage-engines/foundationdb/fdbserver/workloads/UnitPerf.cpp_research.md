# sources/storage-engines/foundationdb/fdbserver/workloads/UnitPerf.cpp

## Purpose
`UnitPerfWorkload` is a simple Flow actor scheduling performance probe. It launches 100,000 sleeping actors and records how many wakeups occur over ten seconds.

## Important APIs, Types, and Functions
The source defines `sleepyActor()`, `unitPerfTest()`, and `UnitPerfWorkload : TestWorkload`, registered as `UnitPerf`. It uses `delay()`, `TraceEvent`, stdout printing, and vector storage of actor futures.

## Control Flow
Only client 0 runs. `unitPerfTest()` initializes a counter, starts 100,000 `sleepyActor(.1, &counter)` futures, waits ten seconds, clears the vector to cancel the actors, traces and prints the final count, and returns.

## State and Persistence Behavior
No database state is read or written. Runtime state is only the counter and actor future vector.

## Dependencies and Integration Points
It integrates with Flow scheduling and the tester workload factory. It is useful as a low-level actor runtime stress probe rather than an FDB database workload.

## Risks and Edge Cases
All actors increment the same stack counter on the Flow event loop; this assumes single-thread actor execution. Launching 100,000 futures is intentionally heavy and can stress memory/scheduling. There are no metrics emitted through `getMetrics()`.

## Test Signals
Trace `Completed` and stdout `Completed: <count>` are the observable performance signals. `check()` always returns true.
