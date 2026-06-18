# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skipmap.rs

Purpose: This nightly `test` benchmark suite measures basic `SkipMap` costs for insertion, forward iteration, reverse iteration, lookup, and insert-then-remove workloads. It uses a deterministic wrapping LCG-like key sequence so each benchmark exercises a fixed set of 1,000 pseudo-random `u64` keys.

Important APIs and functions: The file aliases `crossbeam_skiplist::SkipMap` as `Map`, imports `test::{black_box, Bencher}`, and defines `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove` with `#[bench]`. `black_box` prevents optimizer removal of entries returned by iterators, lookups, and removals.

Control flow: The insert benchmarks build a fresh map inside each `b.iter` invocation. Iteration and lookup benchmarks prepopulate one map before timing and then repeatedly traverse or query it. `insert_remove` populates a fresh map and then removes the same generated keys, unwrapping each removal to assert that benchmark setup remains coherent.

State and persistence behavior: All state is in-memory and per-benchmark. There is no filesystem persistence. The key generator's wrapping arithmetic is the only deterministic workload state.

Dependencies and integration points: It is tied to Rust nightly benchmark support through `#![feature(test)]` and exercises the public `SkipMap` wrapper rather than the lower-level `base::SkipList`.

Risks: Results cover only single-threaded operations on 1,000 keys, so they are not a concurrency scalability signal. The suite also omits comparison with `BTreeMap` or other concurrent maps.

Test signals: It provides performance signals only; `insert_remove` additionally catches unexpected missing keys through `unwrap`.
