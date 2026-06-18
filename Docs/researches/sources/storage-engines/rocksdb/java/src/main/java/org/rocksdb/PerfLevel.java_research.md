# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfLevel.java research

## Purpose

`PerfLevel` exposes native RocksDB performance-counter collection levels to Java. It lets callers trade overhead for count, time, CPU-time, and mutex timing detail.

## Important APIs and types

Constants are `UNINITIALIZED`, `DISABLE`, `ENABLE_COUNT`, `ENABLE_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME_AND_CPU_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME`, and deprecated `OUT_OF_BOUNDS`. `getValue()` returns the native byte. `getPerfLevel(byte)` decodes a byte or throws `IllegalArgumentException`.

## Control flow

Java code passes `getValue()` to native perf-level setters and decodes native bytes through `getPerfLevel()`. `PerfContext` counters then reflect the configured collection level.

## State and persistence behavior

The enum stores only immutable bytes. Perf level changes runtime diagnostics only and has no persistence effect except any external logging performed by callers.

## Dependencies and integration points

It integrates with perf context APIs and native RocksDB perf instrumentation. The deprecated out-of-bounds constant exists only for C++ API parity.

## Risks and test signals

The typo in the exception message is harmless but visible. The important risk is byte parity. Tests should cover all mappings, invalid-byte rejection, deprecated constant behavior, and counter differences between disabled/count/time levels.
