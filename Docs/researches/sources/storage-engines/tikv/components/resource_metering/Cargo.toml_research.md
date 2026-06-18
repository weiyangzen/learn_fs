# sources/storage-engines/tikv/components/resource_metering/Cargo.toml

## Purpose
This manifest defines the `resource_metering` crate, a TiKV component for tagging request execution, collecting resource records, aggregating them, and reporting usage.

## Important APIs, Types, And Functions
The manifest sets package metadata (`name`, `version`, Rust 2021 edition, Apache-2.0) and declares dependencies needed by the public modules: `kvproto` for usage protobufs, `tikv_util` worker/sys/config helpers, `prometheus` metrics, `online_config`, `grpcio`, `futures`, `pin-project`, `pdqselect`, `collections`, `crossbeam`, serde, and logging crates. It also declares a `test-recorder` integration test at `tests/recorder_test.rs` and `rand` as a dev dependency.

## Control Flow
Cargo uses this file to compile the library and integration test. The dependency set supports the flows in `lib.rs`, `model.rs`, recorder, and reporter modules: async wrapping, thread-local registration, online config dispatch, top-K selection, metrics registration, and RPC/report data structures.

## State And Persistence Behavior
The manifest has no runtime state. Its dependency versions and workspace links determine build-time resolution and feature compatibility.

## Dependencies And Integration Points
Workspace dependencies keep the crate aligned with the surrounding TiKV tree. The explicit Prometheus `nightly` feature and `pin-project` match code usage in metrics and `InTags`. The integration test target signals recorder behavior is tested outside the unit-test modules covered here.

## Risks
The crate uses `#![feature(core_intrinsics)]` in `lib.rs`, so compiler/channel compatibility is coupled to TiKV's toolchain. Dependency drift in workspace crates can affect public re-exports and reporter/recorder internals even though this manifest is small.

## Test Signals
The manifest's direct test signal is `[[test]] name = "test-recorder"`, plus unit tests in the crate source files.
