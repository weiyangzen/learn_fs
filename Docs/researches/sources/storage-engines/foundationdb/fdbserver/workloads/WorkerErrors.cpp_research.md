# sources/storage-engines/foundationdb/fdbserver/workloads/WorkerErrors.cpp

## Purpose
`WorkerErrorsWorkload` queries workers for their latest event-log fields and prints them. It is an observability/debug workload rather than a correctness checker.

## Important APIs, Types, and Functions
The workload uses `getWorkers(dbInfo)`, `WorkerDetails`, worker `eventLogRequest.getReply(EventLogRequest())`, `TraceEventFields`, `waitForAll()`, and `timeoutError()`.

## Control Flow
`start()` gets all workers, calls `latestEventOnWorkers()`, and prints each returned `TraceEventFields` as a string. `latestEventOnWorkers()` sends all event-log requests in parallel, waits with a two-second timeout, then collects results.

## State and Persistence Behavior
No database user state is modified. The workload reads worker runtime diagnostic state and writes to stdout.

## Dependencies and Integration Points
It integrates with worker interfaces, quiet database server info, event log request RPCs, and the tester framework.

## Risks and Edge Cases
If any worker does not reply within two seconds, `timeoutError()` fails the whole collection. `check()` always returns true if `start()` completes. The output is printed, not emitted as structured metrics.

## Test Signals
Printed `TraceEventFields` lines are the main artifact. Start-time errors would surface as workload failures; there are no metrics.
