# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerEvents.h

## Purpose
`WorkerEvents.h` declares a helper for collecting the latest trace event fields for a named event across workers.

## Important APIs, Types, And Functions
`WorkerEvents` is a `std::map<NetworkAddress, TraceEventFields>`. `latestEventOnWorkers` takes `std::vector<WorkerDetails>` and an event name, returning an async optional pair of collected events and a set of missing/error worker identifiers.

## Control Flow
The implementation likely sends `EventLogRequest` messages to worker interfaces, collects replies keyed by worker network address, and returns absent data when no events are available.

## State And Persistence Behavior
The helper reads in-memory/latest trace event state on workers. It does not persist anything.

## Dependencies And Integration Points
It depends on tracing fields and `WorkerInterface.actor.h`. It integrates with status/debug tooling and test harnesses that inspect worker event logs.

## Risks And Edge Cases
Workers can fail, omit the requested event, or race log rotation. Network addresses are map keys, so address changes or duplicates can affect aggregation.

## Test Signals
Tests should validate successful collection, missing-event reporting, worker failure handling, and deterministic map contents for multiple workers.
