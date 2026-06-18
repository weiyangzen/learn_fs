<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics.go -->
## sources/storage-engines/pebble/metrics.go

Purpose: defines Pebble's public `Metrics` model, per-level counters, compaction/flush/ingest/WAL/cache/table/blob statistics, and human-readable formatting for diagnostic output.

Important APIs and types: aliases expose cache, filter, throughput, and secondary-cache metrics. `LevelMetrics` tracks LSM size, virtual tables, value-separation references, compaction/flush/ingest counters, read/write bytes, multilevel stats, and additional block-write stats. `Metrics` aggregates subsystem metrics. Helpers include `DiskSpaceUsage`, `NumVirtual`, `VirtualSize`, `ReadAmp`, `Total`, `RemoteTablesTotal`, `SafeFormat`, `String`, `StringForTests`, `AllLevelMetrics.Total`, `AllLevelMetrics.Iter`, and `levelMetricsDelta`.

Control flow: metrics are mostly passive data. `LevelMetrics.Add` accumulates counters; `WriteAmp` divides physical bytes written by logical bytes in. `Metrics.DiskSpaceUsage` sums local WAL, table, blob, options, manifest, and in-progress compaction bytes. `RemoteTablesTotal` adds live/obsolete/zombie table placements and returns shared plus external totals. `String` builds multiple ASCII tables for LSM, compactions, commit pipeline, caches, iterators, file usage, blob values, memory, keys, compression, compression counters, and delete pacer.

State and persistence: metrics represent in-memory snapshots derived from DB state; cumulative counters are monotonic where documented. They do not persist themselves, but they include on-disk sizes and remote-placement accounting.

Dependencies and integration: integrates with manifest levels, cache hit/miss structures, WAL failover stats, table/blob compression stats, Prometheus histograms, manual memory accounting, delete pacer metrics, and `metrics.CountAndSizeByPlacement`.

Risks and edge cases: formatting is broad and brittle to table layout changes. `DiskSpaceUsage` intentionally excludes remote bytes and has a TODO for in-progress remote distinction. `AllLevelMetrics.Total` folds WAL bytes into L0-style flushed bytes to compute write amp, which callers must understand. Category registration is package-global.

Test signals: `metrics_test.go` has golden datadriven output, remote virtual-table regression coverage, WAL write monotonicity, disabled-WAL write amp, and cumulative flushable memory checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics.go -->
