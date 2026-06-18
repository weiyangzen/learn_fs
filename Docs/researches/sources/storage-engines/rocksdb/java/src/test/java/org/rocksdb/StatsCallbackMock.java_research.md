# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/StatsCallbackMock.java

## Purpose

This helper implements `StatisticsCollectorCallback` for tests by counting ticker and histogram callback invocations.

## Important APIs and types

It implements `tickerCallback(TickerType,long)` and `histogramCallback(HistogramType,HistogramData)` from `StatisticsCollectorCallback`.

## Control flow

Each callback increments a public integer counter. No synchronization or filtering is applied.

## State and persistence behavior

The only state is two in-memory counters. There is no native handle and no persisted data.

## Dependencies and integration points

It is used by `StatisticsCollectorTest` to observe whether the collector dispatches both ticker and histogram callbacks.

## Risks and test signals

The helper is intentionally simple. Because counters are not atomic, it is suitable for coarse test assertions after collector activity, not precise concurrency accounting. Signals are counters greater than zero.
