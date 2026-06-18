# sources/storage-engines/pebble/internal/cache/block_map_test.go

Purpose: Benchmarks `blockMap` against Go maps for insert, hit lookup, and miss lookup workloads.

APIs and types: Uses `newBlockMap`, `Put`, `Get`, and `Close` over cache `key` and `entry` values.

Control flow and state: Generates randomized file/offset keys sized to a plausible per-shard block count, then compares repeated map insertions and lookups. Benchmarks close block maps to release manual memory.

Persistence and dependencies: Runtime benchmark only. Depends on rand/v2, runtime keepalive, testing, and base file numbers.

Integration points: Provides performance signal for the cache shard map implementation.

Risks: Benchmarks are not correctness tests and do not exercise eviction or lifecycle beyond close.

Test signals: Useful performance regression signal; functional cache behavior is covered elsewhere.
