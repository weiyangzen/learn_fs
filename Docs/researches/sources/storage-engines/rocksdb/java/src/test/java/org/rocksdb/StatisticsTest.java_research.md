# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/StatisticsTest.java

## Purpose

This suite tests the Java `Statistics` wrapper, including construction with histogram filters, stats-level round trips, ticker reads and resets, histogram data/string reads, full reset, and string rendering.

## Important APIs and types

The suite uses `Statistics`, `StatsLevel`, `TickerType`, `HistogramType`, `HistogramData`, `Options.setStatistics`, and `RocksDB` operations that drive stats.

## Control flow

Tests create statistics directly or attach them to a DB, perform puts/gets, and inspect counters. Ticker reset paths compare pre-reset and post-reset values. Histogram tests verify populated numeric fields and string output after repeated reads/writes.

## State and persistence behavior

Statistics state lives in the native `Statistics` object and accumulates across DB operations while attached to options. Reset mutates counters in place. DB data is temporary and only used to trigger metrics.

## Dependencies and integration points

The suite validates option ownership of statistics, enum mapping, histogram data struct conversion, and native counter reset semantics.

## Risks and test signals

Risks include invalid enum ordinal mapping, stale statistics after reset, zero histograms due to optimized paths, and native handle leaks. Signals are nonzero ticker/histogram fields, reduced counters after reset, and non-null string output.
