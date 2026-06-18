# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyOptionsTest.java

## Purpose

Comprehensive JNI contract coverage for `ColumnFamilyOptions`: copy construction, property parsing, scalar option getters/setters, enum round-trips, nested option objects, compaction filters, memtable/prefix helpers, defaults helpers, and path lists.

## Important APIs, control flow, and dependencies

The test exercises `ColumnFamilyOptions`, `ConfigOptions`, `CompressionOptions`, `CompactionOptionsUniversal`, `CompactionOptionsFIFO`, `DbPath`, `Cache`, `ConcurrentTaskLimiterImpl`, memtable configs, comparator selection, compression and compaction enums, prefix extractor helpers, and `RemoveEmptyValueCompactionFilterFactory`. Most tests create one options object, set a randomly generated or fixed value, and assert the getter returns the same value. Property parsing tests verify valid props, ignored unknown options under `ConfigOptions.setIgnoreUnknownOptions(true)`, and null/empty/unknown failure cases.

## State, persistence, risks, and test signals

No DB is opened, but native option state is allocated and freed repeatedly. Nested Java wrappers such as compression options, compaction options, cache, limiter, filters, and path lists must preserve references correctly across JNI. Risks include stale native field names, signed/unsigned numeric truncation, enum byte mapping drift, and lifetime bugs when options hold native children. Assertions cover every exposed option family plus old-default values and fluent method identity.
