<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs

Purpose: this module is the test-only KMS module registry for the RustFS E2E crate. It documents that KMS tests cover both Local and Vault backends and conditionally includes all KMS test submodules under `#[cfg(test)]`.

Important APIs, types, and functions: it exposes `pub mod common` for test helpers and includes private modules `kms_local_test`, `kms_vault_test`, `kms_comprehensive_test`, `multipart_encryption_test`, `kms_edge_cases_test`, `kms_fault_recovery_test`, `test_runner`, `bucket_default_encryption_test`, and `encryption_metadata_test`.

Control flow: there is no runtime logic. During test builds, Rust compiles the shared KMS helpers and every listed test module; in non-test builds, none of these modules are included.

State and persistence: no state is stored here. It controls compilation reachability for KMS test state owned by child modules.

Dependencies and integration points: integrates with the crate root `lib.rs`, Rust `#[cfg(test)]` conditional compilation, and Rust module resolution. `common` is public only within the test build so sibling and possibly external test code can reuse it.

Risks: adding a KMS test file without listing it here excludes it from test compilation. Conversely, listing a module with expensive tests means it is compiled even when tests are filtered. This file does not apply feature flags for Vault/local availability; runtime tests must handle skips.

Test signals: successful compilation of this module proves all named KMS test files resolve. Actual behavioral signals come from child module tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/mod.rs -->
