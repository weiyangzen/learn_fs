# sources/storage-engines/tikv/tests/Cargo.toml

## Purpose
This manifest defines TiKV's private `tests` crate. It wires integration/failpoint tests and benchmark targets for raftstore, coprocessor executors, hierarchy, misc, deadlock detector, and memory quota benchmarks.

## Important APIs, Types, and Functions
The manifest declares test targets `failpoints` and `integrations`, and bench targets with mixed harness modes. Feature flags expose failpoints, test exports, test engine choices, allocators, CPU portability/SSE, mem profiling, and Docker-specific tests.

## Control Flow
Cargo selects targets and features from this file. Default features enable failpoints, testexport, RocksDB KV testing, and raft-engine raft testing. Criterion-style benchmarks use `harness = false`; the `misc` bench keeps the Rust test harness and nightly `test` feature.

## State and Persistence Behavior
The file has no runtime state. It controls compile-time dependency resolution and therefore which TiKV internal APIs are visible to tests and benchmarks.

## Dependencies and Integration Points
Dependencies include workspace crates for storage, raftstore, PD, engines, query executors, server/service, resource control, and test helpers. Dev dependencies include Criterion, perf events on Linux x86_64, engine/test crates, backup/import helpers, and JSON/test utilities.

## Risks and Test Signals
Risks are feature drift, duplicated dependencies, target-specific dev-dependency breakage, and bench target mismatches. A useful signal is successful `cargo test -p tests` or selected bench compilation under the default feature set and under alternate engine/allocator feature combinations.
