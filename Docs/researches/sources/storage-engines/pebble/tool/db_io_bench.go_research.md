## sources/storage-engines/pebble/tool/db_io_bench.go

Purpose: implements `db io-bench`, a random read benchmark over current SSTable backing objects, intended to measure IO-size-to-latency relationships, especially for object storage.

Important APIs/types/functions: `benchIO` records readable index, aligned offset, read size, and measured elapsed time. `runIOBench` parses sizes, opens the DB, opens benchmark tables, generates IOs, runs workers, and prints stats. `genBenchIOs` chooses random 1 MiB blocks across objects and creates one IO per requested size for each chosen block. `openBenchTables` collects unique backing SST numbers from L5/L6 by default or all levels with `--all-levels`, opens object readables, and keeps only objects at least 1 MiB. `parseIOSizes` parses comma-separated KiB sizes, requiring each to divide 1 MiB and be no larger than 1 MiB. `performIOs` uses per-readable `ReadHandle`s and a 1 MiB buffer. `getStats` calculates average, stddev, and p10/p50/p90/p95/p99.

Control flow: IOs for all sizes are shuffled together, then divided among `ioParallelism` goroutines by remaining-average partitioning. Each worker performs sequential reads over its slice and writes elapsed durations into the shared `ios` backing array. Results are regrouped by size after all workers finish.

State and persistence: opens the DB read-only and table objects for reading. It does not persist benchmark artifacts. Randomness is global `rand/v2`, so benchmark sequences are intentionally non-deterministic.

Dependencies and integration: uses `dbT.openDB`, Pebble `SSTables`, DB object provider, `objstorage.Readable`, and command flags installed by `db.go`.

Risks: no explicit validation prevents zero or negative `io-parallelism`; division by zero or panic is possible if misconfigured. `genBenchIOs` assumes at least one 1 MiB block and may panic if object totals are inconsistent, though `openBenchTables` filters too-small objects. Shared writes are safe by disjoint slices, but worker errors only print and do not fail the command. It benchmarks backing objects, so virtual SST sharing is deduplicated.

Test signals: no direct test in this subset; coverage is primarily through compilation and command registration.
