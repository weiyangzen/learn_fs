# sources/storage-engines/tikv/tests/benches/misc/serialization/mod.rs

Purpose: module shim for misc serialization benchmarks. It exposes `bench_serialization` to the bench harness.

Important APIs and functions: only `mod bench_serialization;` is declared.

Control flow: compile-time module inclusion only; benchmark discovery happens through `#[bench]` functions inside the child module.

State and persistence: none.

Dependencies and integration: integrates `bench_serialization.rs` under the misc benchmark tree.

Risks and test signals: risk is limited to accidental module removal causing all serialization benches to disappear from the suite.
