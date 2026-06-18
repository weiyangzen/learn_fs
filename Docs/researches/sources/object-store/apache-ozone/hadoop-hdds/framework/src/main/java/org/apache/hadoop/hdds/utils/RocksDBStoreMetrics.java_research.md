# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RocksDBStoreMetrics.java

## Purpose
`RocksDBStoreMetrics` exports RocksDB statistics, properties, SST layout, and sequence metrics through Hadoop Metrics2. It supports both per-column-family metrics and aggregated counters for selected RocksDB properties.

## Important APIs and Types
`create` registers or reuses a metrics source named with `ROCKSDB_CONTEXT_PREFIX + dbName`. `getMetrics` delegates to `getHistogramData`, `getTickerTypeData`, `getDBPropertyData`, and `getLatestSequenceNumber`. Helpers compute live SST file counts/sizes per level and export them as metrics.

## Control Flow and State
Constructor stores `Statistics`, `RocksDatabase`, context name, known histogram attributes, and precomputes Prometheus-style property suffixes. Histogram collection reflects over `HistogramData` getters for average/median/p95/p99/stddev/max while skipping BLOB DB metrics. Property collection iterates extra column families, reads `rocksdb.*` properties, and aggregates selected values.

## Persistence, Dependencies, and Integration
No persistence is created, but it reads live RocksDB state. Dependencies include RocksDB `Statistics`, `TickerType`, `HistogramType`, `LiveFileMetaData`, HDDS `RocksDatabase`, and Metrics2. It is registered by `RDBStore` when RocksDB metrics are enabled.

## Risks and Test Signals
Reflection can log noisy errors if RocksDB changes histogram accessors. Property values are parsed as longs and can fail for unavailable properties. Raw `HashMap` use is unchecked. Tests should cover duplicate registration reuse, BLOB metric exclusion, null statistics, per-CF and aggregate property emission, SST level aggregation, and latest sequence error handling.
