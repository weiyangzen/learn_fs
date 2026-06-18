# sources/storage-engines/tikv/tests/benches/misc/writebatch/mod.rs

Purpose: module shim for write batch benchmarks.

Important APIs and functions: declares `mod bench_writebatch;`.

Control flow: compile-time module inclusion only.

State and persistence: none in this file; child benchmarks create temp RocksDB instances.

Dependencies and integration: links writebatch benchmarks to the misc bench harness.

Risks and test signals: removing this file’s module declaration drops the write batch benchmark family.
