# sources/storage-engines/foundationdb/fdbserver/workloads/LogMetrics.cpp

## Purpose
Workload that temporarily increases system metric logging frequency and runs `systemMonitor` at that rate, then restores the default metric rate.

## Important APIs, types, and functions
`LogMetricsWorkload` uses options `logAt`, `logDuration`, `logsPerSecond`, and `dataFolder`. `setSystemRate` sends `SetMetricsLogRateRequest` to all workers returned by `getWorkers(dbInfo)` and writes the `fastLoggingEnabled` system key. `_start` controls the timing.

## Control flow
Client 0 waits `logAt`, sets worker and storage metric rates to `logsPerSecond`, runs `recurring(&systemMonitor, 1.0 / logsPerSecond)` for `logDuration`, then calls `setSystemRate` with `1.0` to restore normal logging.

## State and persistence behavior
The workload writes the `fastLoggingEnabled` system key in a self-conflicting transaction and sends in-memory rate changes to worker interfaces. It does not write user data.

## Dependencies and integration points
Depends on worker interface discovery, metrics log-rate RPCs, system monitor infrastructure, `ServerDBInfo`, `QuietDatabase` headers, system key access, and transaction retry semantics.

## Risks and test signals
`check` always returns true and no metrics are exported. Risks are increased trace/log volume, partial worker delivery because sends are fire-and-forget, and restoring with a floating value converted to `uint32_t`. Signals are trace events around rate changes and absence of actor errors.
