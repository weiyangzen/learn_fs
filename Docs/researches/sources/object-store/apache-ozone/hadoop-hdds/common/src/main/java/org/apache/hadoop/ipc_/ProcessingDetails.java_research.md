
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProcessingDetails.java

## Purpose

`ProcessingDetails` records per-call timing for each IPC processing phase. It feeds scheduler cost/backoff logic, detailed metrics, and diagnostic logging.

## Important APIs, types, and functions

The `Timing` enum covers `ENQUEUE`, `QUEUE`, `HANDLER`, `PROCESSING`, lock-free/wait/shared/exclusive subphases, and `RESPONSE`. The package-private constructor fixes the internal `TimeUnit`. `get()`, `get(..., TimeUnit)`, `set()`, `set(..., TimeUnit)`, and `add()` manipulate timing values. `toString()` emits all timings as lower-case `*Time=` fields.

## Control flow

IPC code creates a details object for a call, records durations as the call moves through reader, queue, handler, processing, lock, and response stages, then passes the object to scheduler and metrics paths. `get()` clamps negative values to zero to handle rare `nanoTime` anomalies.

## State and persistence behavior

State is a per-call `long[]` indexed by enum ordinal plus the internal value time unit. Nothing is persisted.

## Dependencies and integration points

`DecayRpcScheduler` reads `QUEUE` and `PROCESSING` in `RpcMetrics.TIMEUNIT`; cost providers can read any timing. Ozone integration tests include `testProcessingDetails()` in filesystem test coverage.

## Risks and test signals

Enum ordinal indexing means reordering `Timing` values changes serialized/logical interpretation inside the object. Tests should cover unit conversion, additive updates, negative-value clamping, `toString()` field order, and the invariant that `PROCESSING` equals lock subphase totals when maintained by callers.
