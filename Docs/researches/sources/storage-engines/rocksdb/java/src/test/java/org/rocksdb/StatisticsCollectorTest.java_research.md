# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/StatisticsCollectorTest.java

## Purpose

This test validates the Java `StatisticsCollector`, which periodically polls RocksDB `Statistics` and invokes Java callbacks for ticker and histogram data.

## Important APIs and types

The file uses `Statistics`, `Options.setStatistics`, `StatsCollectorInput`, `StatisticsCollector`, and `StatsCallbackMock`.

## Control flow

The test opens a DB with attached statistics, retrieves the same stats object from options, constructs a callback input, starts a collector with a 100 ms interval, sleeps for one second, asserts both callback counters increased, then shuts the collector down.

## State and persistence behavior

No persistent DB data is required. State is runtime statistics counters and a background Java collection thread. Proper shutdown is part of the behavior under test.

## Dependencies and integration points

This covers Java callback dispatch, statistics ownership through `Options`, background scheduling, and clean shutdown.

## Risks and test signals

Risks include collector thread leaks, callbacks not firing, histogram/ticker enum conversion failures, and races from timing. Signals are callback counts greater than zero and `shutDown(1000)` completion.
