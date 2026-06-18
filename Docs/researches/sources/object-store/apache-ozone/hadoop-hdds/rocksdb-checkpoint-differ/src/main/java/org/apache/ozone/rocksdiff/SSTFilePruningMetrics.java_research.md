<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java

Purpose: Hadoop metrics source for monitoring SST backup value-pruning activity in `RocksDBCheckpointDiffer`.

Important APIs/types/functions: `create(dbLocation)` registers a metrics source named from the class plus sanitized DB location. Metrics include total files pruned, files pruned in last batch, total skipped/removed files, compactions processed, prune queue size, and pruning failures. Public update/getter methods mutate and read these counters/gauges. `getMetrics` snapshots all metrics to a collector.

Control flow and state: Metrics are registered through `DefaultMetricsSystem`. Batch updates increment counters/gauges after pruning runs. `unRegister` removes the source during differ close.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer` constructor, `close`, compaction queue updates, successful pruning batches, and pruning failure handling.

Risks: Source-name sanitization replaces path separators, colon, and whitespace, but very long DB paths can still produce long metric names. Metrics fields are initialized by Hadoop metrics injection/registration; using an instance before registration would be unsafe.

Test signals: Should verify registration/unregistration, sanitized names, queue updates, batch counter increments, and failure counter increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/SSTFilePruningMetrics.java -->
