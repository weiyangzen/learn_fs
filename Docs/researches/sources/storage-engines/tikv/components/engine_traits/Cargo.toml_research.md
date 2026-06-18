# sources/storage-engines/tikv/components/engine_traits/Cargo.toml

Purpose: Defines the `engine_traits` crate package metadata, optional features, and dependency boundary for TiKV's generic storage-engine abstraction.

Important APIs and control flow: Features expose `failpoints` and `testexport`. Dependencies include shared TiKV crates for collections, encryption, error codes, filesystem rate limiting, keys, protobufs, Raft, logging, tracking, utilities, and transaction types. Dev dependencies add `rand` and `toml`.

State, persistence, and dependencies: The manifest persists no runtime state, but its dependency graph enforces the important design rule that `engine_traits` should not depend on RocksDB/TiRocks concrete bindings.

Integration points, risks, and test signals: All engine implementations and generic users depend on this crate. Risks include accidentally introducing concrete engine dependencies, feature skew with implementor crates, or nightly feature requirements in `lib.rs` constraining toolchains. Test signals are workspace build resolution, feature-specific builds, and conformance tests from `engine_traits_tests`.
