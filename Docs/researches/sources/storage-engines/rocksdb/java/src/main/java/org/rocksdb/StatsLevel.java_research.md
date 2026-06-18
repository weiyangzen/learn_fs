# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsLevel.java

## Purpose
`StatsLevel` maps RocksDB statistics collection levels into Java, controlling how much timing/counter work the native engine performs.

## Important APIs and Types
Values are `EXCEPT_DETAILED_TIMERS`, `EXCEPT_TIME_FOR_MUTEX`, and `ALL`, each with a byte mapping. `getValue()` returns the native byte and `getStatsLevel(byte)` maps native bytes back to Java.

## Control Flow
Reverse mapping linearly scans enum values and throws `IllegalArgumentException` on unknown input.

## State and Persistence Behavior
No mutable state exists. Stats level affects native in-memory statistics behavior when applied through `Statistics.setStatsLevel`.

## Dependencies and Integration Points
`Statistics` uses it for `statsLevel()` and `setStatsLevel()`. Documentation warns that collecting mutex timings can reduce scalability.

## Risks and Test Signals
Tests should cover every byte mapping, invalid byte failures, and performance behavior at `ALL`. Native/Java enum drift would break `Statistics.statsLevel()`.
