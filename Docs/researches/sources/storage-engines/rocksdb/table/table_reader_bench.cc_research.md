# sources/storage-engines/rocksdb/table/table_reader_bench.cc

Purpose: standalone benchmark for measuring table-reader point lookup and iterator performance, either directly through a table reader or through a DB.

Important APIs/types/functions: `MakeKey` builds deterministic user or internal keys; `Now` selects microsecond/nanosecond timing; `TableReaderBenchmark` builds/populates data, opens table or DB, runs randomized get/iterator workloads, records a `HistogramImpl`, and prints results. `main` parses gflags and selects block-based, plain, or cuckoo table factory options.

Control flow: when `through_db` is false, the benchmark builds a table file directly with `TableBuilder`, writes about `num_keys1 * num_keys2` keys, reopens it through `NewTableReader`, then performs repeated randomized lookups or range iterations. When `through_db` is true, it opens a temporary DB, writes keys, flushes, and benchmarks DB APIs. Iterator mode verifies expected sequential keys.

State and persistence behavior: creates temporary per-thread table/DB paths, writes benchmark data, and deletes/destroys them at the end. No production state is modified.

Dependencies/integration points: integrates gflags, RocksDB DB APIs, table factories, file readers/writers, `GetContext`, internal iterators, test utilities, histograms, and env/system clock.

Risks: compiled fallback without gflags only prints an error. Benchmark asserts on iterator count mismatches. Direct table-reader mode uses internal keys, so `MakeKey` must match table expectations. Some flag combinations, especially prefix/plain-table choices, affect validity and measured behavior.

Test signals: this is not a correctness test but provides performance and smoke coverage for direct table-reader get/iterator paths across table factories.
