# sources/storage-engines/foundationdb/fdbserver/core/WorkerEvents.cpp

## sources/storage-engines/foundationdb/fdbserver/core/WorkerEvents.cpp

Purpose: queries workers for their latest trace event fields, optionally filtered by event name, and returns both results and failed workers.

Important API: `latestEventOnWorkers`.

Control flow and state: for each `WorkerDetails`, the actor builds an `EventLogRequest`, sends it to the worker's `eventLogRequest` stream, wraps it with `timeoutError(..., 2.0)` and `errorOr`, then waits for all futures. It builds a `WorkerEvents` map keyed by worker address. Failed or timed-out requests add the address string to the failed set and store empty `TraceEventFields`; successful requests store returned fields. Only actor cancellation should escape because per-worker errors are captured.

Dependencies and integration: depends on `WorkerEvents.h`, worker interfaces, Flow futures, event log RPCs, trace field serialization, and address formatting. It is useful for status, diagnostics, and latest-role/event inspection across workers.

Risks and tests: the fixed two-second timeout can report slow workers as failed. Empty event names request default latest events. Tests should cover all-success, partial timeout/error, empty event names, named event lookup, and cancellation propagation.
