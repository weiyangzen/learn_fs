# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStatsRecorder.java

## Purpose

`CacheStatsRecorder` is a package-private atomic counter helper for table cache metrics. The complete 58-line source was read for this report.

## Important APIs, Types, and Functions

It owns `AtomicLong` counters for hits, misses, and iterations. Methods are `recordHit`, `recordMiss`, `recordValue`, `recordIteration`, and `snapshot`.

## Control Flow

`recordValue` treats a null `CacheValue` as a miss and a non-null value, including a tombstone, as a hit. `snapshot` returns a `CacheStats` object with current counter values.

## State and Persistence Behavior

State is in-memory and thread-safe through atomic counters. It has no persistence.

## Dependencies and Integration Points

It depends on `AtomicLong`, `CacheValue`, and `CacheStats`. Full and partial cache implementations call it on lookups and iterator creation.

## Risks and Edge Cases

Tombstone entries count as hits because the cache did contain information. Counters are monotonically increasing and do not reset.

## Test Signals

Tests should verify null/non-null hit accounting, iteration accounting, snapshot consistency under concurrent calls, and tombstone hit behavior.
