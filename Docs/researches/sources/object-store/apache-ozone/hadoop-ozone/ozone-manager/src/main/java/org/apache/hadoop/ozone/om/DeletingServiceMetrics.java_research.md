# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeletingServiceMetrics.java

## Purpose

`DeletingServiceMetrics` registers and updates Hadoop metrics for OM key and directory deletion background services.

## Important APIs and Types

- `create()` registers the metrics source; `unregister()` removes it.
- Increment/update methods cover directory deletion totals, key deletion totals, purge counts, moved subfiles/subdirectories, last-run timestamps, AOS/snapshot last-run metrics, interval reclaimed metrics, and last AOS purge transaction info.
- `getLastAOSTransactionInfo` and `setLastAOSTransactionInfo` manage a monotonic `TransactionInfo`.
- `resetDirectoryMetrics` is visible for tests.

## Control Flow

Most methods directly increment or set `MutableGaugeLong` fields. Interval metrics call `checkAndResetMetrics`, which initializes `metricsResetTimeStamp` on first use and resets reclaimed keys/size if more than one day has elapsed. `setLastAOSTransactionInfo` synchronizes, compares the new transaction with the current one, and only updates gauges if it advances.

## State and Persistence

All state is process-local metrics gauge state registered in `DefaultMetricsSystem`. It resets on OM restart. The last AOS purge transaction metrics are used by deletion services to avoid starting a subsequent background run before the previous purge has been flushed, but they are metrics-backed process state rather than durable metadata.

## Dependencies and Integration Points

It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `MutableGaugeLong`, `TransactionInfo`, and OM background services such as key deleting and directory deleting services.

## Risks and Edge Cases

Metrics fields are injected/initialized by the metrics system; direct construction outside `create()` can leave gauges null. Most updates are not synchronized, while transaction update is synchronized. The 24-hour reset is based on epoch seconds and only happens when interval metrics are updated. Gauges are used for cumulative counters, which is common in metrics2 but can surprise readers expecting counters.

## Test Signals

Tests should cover registration/unregistration, increment methods, interval reset behavior, monotonic transaction update, resetDirectoryMetrics, and service code updating last-run metrics with correct AOS/snapshot separation.
