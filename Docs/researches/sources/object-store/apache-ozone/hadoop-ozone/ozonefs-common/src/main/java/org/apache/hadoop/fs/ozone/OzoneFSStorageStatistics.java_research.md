<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java

## Purpose
Hadoop `StorageStatistics` implementation for Ozone filesystem operation and object counters.

## Important APIs, types, and functions
The class extends `StorageStatistics`, implements `Iterable<LongStatistic>`, initializes an `EnumMap<Statistic, AtomicLong>`, exposes `incrementCounter`, `getLongStatistics`, `getLong`, `isTracked`, `reset`, and a testing `snapshot`.

## Control flow
Construction creates a zero counter for every `Statistic`. `incrementCounter` atomically updates a counter. Iteration exposes immutable entry traversal as Hadoop long statistics.

## State and persistence behavior
All state is in-memory per filesystem instance. Counters are resettable and do not persist across process or filesystem lifecycle.

## Dependencies and integration points
Used by full Hadoop 3 filesystems and adapter implementations. It bridges `Statistic` enum symbols to Hadoop storage statistics consumers and reports the Ozone URI scheme.

## Risks and test signals
Counters can be incomplete if filesystem methods forget to call `incrementCounter` or adapter hooks are not wired. Tests should verify tracked symbols, reset behavior, iterator behavior, and counter increments across high-level filesystem and low-level object operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java -->
