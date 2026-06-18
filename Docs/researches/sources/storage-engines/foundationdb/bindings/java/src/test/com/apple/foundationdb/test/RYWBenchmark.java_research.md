# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RYWBenchmark.java

Purpose: benchmark read-your-writes cache behavior within one Java transaction.

Important APIs and flow: a single transaction is created in `testPerformance`, seeded with deterministic keys by `insertData`, and reused for requested enum tests. Tests measure repeated cached gets of one key, sequential cached gets, full range reads from the transaction cache, range reads after point clears, range reads after clear ranges, and interleaved set/get increments on one key. Median results are written as KPIs.

State and persistence: `insertData` clears user space, sets keys in the transaction, and the transaction is canceled at the end, so the benchmark targets in-memory RYW behavior rather than committed storage state. It still mutates transaction state heavily. Risks include destructive clear staged in a transaction, cache growth, tests interacting through one reused transaction, and argument subspace inconsistencies in clear calls. Signal is KPI output and errors captured by `AbstractTester`.
