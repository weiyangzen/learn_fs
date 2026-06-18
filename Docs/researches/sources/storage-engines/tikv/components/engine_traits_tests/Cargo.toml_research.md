# sources/storage-engines/tikv/components/engine_traits_tests/Cargo.toml

Purpose: Defines the engine-agnostic conformance test crate for `engine_traits`.

Important APIs and control flow: Default features select RocksDB KV and raft-engine backends via `engine_test`. Additional features select RocksDB engine pairs or panic engines. Dependencies include encryption export, `engine_test`, `engine_traits`, panic recovery hooks, tempfile, and test utilities. Doctests are disabled for the lib target.

State, persistence, and dependencies: The manifest persists no runtime state but controls which concrete test backend is instantiated.

Integration points, risks, and test signals: This crate is the shared behavioral gate for implementors. Risks include feature combinations hiding backend failures, tests covering only basic semantics, and dependency on `engine_test` constructors. Running this crate under each feature set is the primary signal.
