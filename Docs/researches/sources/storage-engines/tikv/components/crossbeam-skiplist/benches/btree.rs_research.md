# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/btree.rs

Purpose: baseline benchmark suite using `std::collections::BTreeMap` for ordered-map operations comparable to skiplist workloads.

Important APIs and types: benchmark functions `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove`; `Map` alias to `BTreeMap`; `test::Bencher` and `black_box`.

Control flow: each benchmark generates deterministic pseudo-random `u64` keys via `wrapping_mul(17).wrapping_add(255)`. Insert and insert/remove benchmarks create a fresh map per iteration; iteration and lookup benchmarks prepopulate once and repeatedly traverse or query.

State and persistence: in-memory benchmark data only.

Dependencies and integration: uses Rust nightly `test` benchmark harness. Provides ordered-map baseline for the forked skiplist benches.

Risks: deterministic key generation can produce distribution-specific results. This baseline is single-threaded and does not model concurrent skiplist advantages. It uses the unstable `test` feature.

Test signals: performance baseline for ordered iteration, reverse iteration, lookup, insertion, and removal.
