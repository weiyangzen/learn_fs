# sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs

Purpose: module aggregator for the `reliant` test suite. It declares the child test modules that depend on live RustFS services, local lock shims, or specialized e2e harness behavior.

Important APIs and functions: this file exposes no functions or types. It contains `mod` declarations for `conditional_writes`, `get_deleted_object_test`, `grpc_lock_client`, `grpc_lock_server`, `head_deleted_object_versioning_test`, `head_tls_bodyless_test`, `lifecycle`, `lock`, `node_interact_test`, and `sql`.

Control flow: Rust module loading pulls these files into the test crate. Each child file gates itself with `#![cfg(test)]` or defines tests, so this module is a compile-time integration point rather than a runtime dispatcher.

State and persistence: no runtime state or persistence. The presence of module declarations controls compilation and availability of test helpers, including the gRPC lock client/server modules used by `lock.rs`.

Dependencies and integration points: the e2e test crate module tree. It is the bridge between the crate root and the reliant tests.

Risks: adding a source file under `reliant` without updating this file means it will not compile or run. Removing or renaming child files without updating declarations breaks the test crate. It intentionally includes helper modules (`grpc_lock_client`, `grpc_lock_server`) that are not standalone tests but are required by `lock.rs`.

Test signals: no direct assertions; its signal is compile-time inclusion of the listed test modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/mod.rs -->
