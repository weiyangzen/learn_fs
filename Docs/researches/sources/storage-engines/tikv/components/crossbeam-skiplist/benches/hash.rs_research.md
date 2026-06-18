# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/hash.rs

Purpose: baseline benchmark suite using `std::collections::HashMap` for unordered map operations comparable to skiplist insertion and lookup workloads.

Important APIs and types: benchmark functions `insert`, `iter`, `lookup`, and `insert_remove`; `Map` alias to `HashMap`; `test::Bencher` and `black_box`.

Control flow: benchmarks use the same deterministic pseudo-random `u64` sequence as the BTreeMap and skiplist benches. Insert and insert/remove create fresh maps; iter and lookup use a prepopulated map.

State and persistence: in-memory benchmark data only.

Dependencies and integration: nightly `test` benchmark harness. Serves as an unordered baseline; it lacks `rev_iter` because `HashMap` has no ordered reverse traversal.

Risks: `HashMap` iteration ordering is intentionally unspecified, so iteration results are not comparable to ordered traversal semantics. The workload is single-threaded and does not represent concurrent use.

Test signals: performance baseline for hash-table insert, iterate, lookup, and remove operations.
