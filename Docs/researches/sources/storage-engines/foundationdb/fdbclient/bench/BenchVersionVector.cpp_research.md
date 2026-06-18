# sources/storage-engines/foundationdb/fdbclient/bench/BenchVersionVector.cpp

Purpose: measures `VersionVector::getDelta` cost as the number of tracked tags and requested deltas grows.

Important APIs and control flow: initializes a `VersionVector` with a base version, sets monotonically increasing versions for `tags` tags, then each iteration updates one rotating tag and calls `getDelta(version - j, delta)` for `numDeltas` recent versions.

State and persistence: all state is in-memory `VersionVector` data. The benchmark models serialization/replication metadata computation but does not persist it.

Dependencies and integration: includes Google Benchmark and `fdbclient/VersionVector.h`; uses `Tag`, `Version`, and `benchmark::DoNotOptimize`.

Risks: all tags use locality `0`, so multi-locality lookup/compression behavior is not measured here. The version progression is regular and may be friendlier than production patterns.

Test signals: registered ranges cover 16 to 1024 tags and 1 to 1024 delta calls, reporting aggregate item processing and custom counters for tags and delta count.
