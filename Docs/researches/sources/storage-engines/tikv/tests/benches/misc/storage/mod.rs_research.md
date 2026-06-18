# sources/storage-engines/tikv/tests/benches/misc/storage/mod.rs

Purpose: module aggregator for misc storage benchmarks.

Important APIs and functions: includes `incremental_get`, `key`, `mvcc_reader`, and `scan`.

Control flow: compile-time module wiring only.

State and persistence: none in this file; child modules create RocksDB-backed test storage as needed.

Dependencies and integration: connects storage microbenchmarks to the misc bench harness.

Risks and test signals: accidental omission disables the corresponding benchmark module.
