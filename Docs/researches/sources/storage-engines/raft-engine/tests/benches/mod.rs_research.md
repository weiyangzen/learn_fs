# sources/storage-engines/raft-engine/tests/benches/mod.rs

Purpose: this is the Criterion bench harness entry point for raft-engine integration benchmarks.

Important APIs and types: it imports `criterion_main`, declares `mod bench_recovery`, and invokes `criterion_main!(bench_recovery::benches)`.

Control flow: when Cargo runs this bench target, Criterion uses this module as the main function and executes the benchmark group exported from `bench_recovery.rs`.

State and persistence behavior: no state is stored here. Temporary data is managed by the benchmark modules it invokes.

Dependencies and integration points: depends on Criterion and the sibling `bench_recovery` module. `extern crate libc` is present for benchmark/test environment linkage even though this file does not use it directly.

Risks and invariants: all benchmark groups must be wired through this file to run. If `bench_recovery::benches` changes name or is not exported by `criterion_group!`, the harness fails to compile.

Test signals: successful bench harness compilation confirms Criterion wiring. Runtime signals come from the included benchmark groups.
