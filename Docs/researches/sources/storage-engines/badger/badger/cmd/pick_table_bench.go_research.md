# sources/storage-engines/badger/badger/cmd/pick_table_bench.go

Purpose: implements `badger benchmark picktable`, a benchmark for iterator table selection logic.

Important APIs and flow: it opens Badger managed, derives table boundaries from `db.Tables`, constructs mock in-memory tables with `table.NewTableBuilder` and `OpenInMemoryTable`, initializes a local `levelHandler`, samples keys using `getSampleKeys`, and runs `testing.Benchmark(BenchmarkPickTables)`. The local `iteratorOptions`, `compareToPrefix`, and `pickTables` mirror production iterator logic with prefix and `SinceTs` filtering.

State and persistence: reads an existing DB and creates transient in-memory tables; optional CPU profile writes to a file. Dependencies are Badger table APIs, testing benchmark harness, pprof, and read-benchmark key sampling. Risks: the copied production logic can drift from real iterator code, global `keys` and `handler` make benchmark state package-global, and generated mock table ranges are synthetic. Test signals are benchmark output, CPU profile generation, and periodic diff checks against production `levelHandler.pickTables`.
