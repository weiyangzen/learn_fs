# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollectorCallback.java

## Purpose
`StatisticsCollectorCallback` defines the callback contract used by `StatisticsCollector` to deliver sampled ticker and histogram values.

## Important APIs and Types
The interface declares `tickerCallback(TickerType, long)` and `histogramCallback(HistogramType, HistogramData)`.

## Control Flow
Implementations are invoked synchronously on the collector's executor thread for each sampled metric.

## State and Persistence Behavior
The interface owns no state. Implementations decide whether to store, aggregate, export, or discard metric samples.

## Dependencies and Integration Points
It depends on RocksDB metric enums and `HistogramData`; `StatsCollectorInput` pairs a callback with a `Statistics` object.

## Risks and Test Signals
Tests should validate callback ordering only if callers depend on it and should exercise implementations under concurrent collectors. The contract states thread safety is the user's responsibility when a callback instance is shared.
