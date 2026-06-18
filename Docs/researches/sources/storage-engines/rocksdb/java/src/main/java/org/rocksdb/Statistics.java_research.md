# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Statistics.java

## Purpose
`Statistics` is the Java owner/wrapper for RocksDB's native statistics object, exposing ticker counters, histograms, stats-level configuration, reset, copying, and formatted output.

## Important APIs and Types
Constructors allocate empty statistics, copy another `Statistics`, or allocate/copy while ignoring selected `HistogramType` values. Public APIs include `statsLevel()`, `setStatsLevel(StatsLevel)`, `getTickerCount(TickerType)`, `getAndResetTickerCount(TickerType)`, `getHistogramData(HistogramType)`, `getHistogramString(HistogramType)`, `reset()`, and `toString()`.

## Control Flow
Public calls assert ownership then pass enum byte values to native functions. Constructors load the RocksDB JNI library before allocation. `toArrayValues` converts `EnumSet<HistogramType>` into native byte identifiers.

## State and Persistence Behavior
The native statistics object accumulates in-memory counters and histograms for a DB/options configuration. It is not persisted by this wrapper. `reset` clears native statistics, and `getAndResetTickerCount` atomically observes and clears one ticker.

## Dependencies and Integration Points
It extends `RocksObject` and integrates with `DBOptions#statistics()`, `Options`/`DBOptions` attachment, `TickerType`, `HistogramType`, `HistogramData`, and `StatsLevel`.

## Risks and Test Signals
Tests should verify library loading, copy semantics, ignored histogram behavior, enum byte mapping, reset behavior, and use-after-close failures. Performance-sensitive tests should distinguish stats levels because `StatsLevel.ALL` enables expensive timing in mutex paths.
