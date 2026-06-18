# sources/storage-engines/foundationdb/fdbclient/bench/BenchVersionedMap.cpp

Purpose: comprehensive Google Benchmark coverage for `VersionedMap` point operations, scans, erase behavior, string key cost, and retained historical-version behavior.

Important APIs and types: `VersionedMapHarness<K>` adapts `VersionedMap<K,int>` to benchmark-style operations. `IntFixture` and `StringRefFixture` generate deterministic random keys and optionally populate/sort/unique them. Benchmarks cover insert, find, lower/upper bound, last-less variants, scan, sorted find, erase, and a manual-time multiversion workload.

Control flow: each operation benchmark creates a fixture outside timed sections, runs the measured operation over all keys, asserts correctness where applicable, and tears down outside timing. The multiversion benchmark creates 50,000 versions, mutates latest state, performs historical reads/scans, and periodically `compact`s and `forgetVersionsBefore`s older versions.

State and persistence: state is in-memory persistent-version tree data. There is no durable persistence, but it models version-retention structures used throughout FoundationDB.

Dependencies and integration: includes `fdbclient/VersionedMap.h`, deterministic Flow random seeding, STL random/shuffle/sort, and Google Benchmark.

Risks: million-key fixtures are heavy; benchmark resource use is significant. Deterministic seeds stabilize tree shape, which improves comparison but may hide worst-case random variation. String keys are fixed length 100.

Test signals: assertions validate lookup/scan/erase correctness during benchmark runs; manual counters expose operation-specific kops in the multiversion benchmark.
