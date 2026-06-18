<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/lib.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/lib.rs

Purpose: this is the crate root for RustFS E2E tests. It registers common helpers and a broad set of test modules covering object semantics, IAM/policy behavior, KMS, listing/versioning, object lock, cluster behavior, checksums, healing, replication, object lambda, and other regressions.

Important APIs, types, and functions: `pub mod common` exposes shared E2E utilities under `#[cfg(test)]`, and `pub mod tls_gen` is always public. Most entries are `#[cfg(test)] mod ...;` declarations, including the files in this subset: `kms`, `existing_object_tag_policy_test`, `group_delete_test`, `head_object_range_test`, `head_object_consistency_test`, `heal_erasure_disk_rebuild_test`, and `list_object_versions_metadata_extension_test`.

Control flow: there is no executable control flow beyond Rust module compilation. In test builds, all listed modules are compiled and their `#[tokio::test]` cases become discoverable by the Rust test harness. Non-test builds exclude nearly all E2E modules and common helpers.

State and persistence: no runtime state is stored here. It controls which test modules can create state in their own environments. Ordering in this file does not order test execution; serial behavior is controlled inside individual tests.

Dependencies and integration points: integrates with Cargo/Rust module resolution, the Rust test harness, and every declared source file. It is the top-level inclusion point that makes E2E regression tests part of the crate.

Risks: a missing module declaration silently prevents a test file from compiling/running. Broad unconditional `#[cfg(test)]` inclusion means expensive or environment-dependent tests are compiled for test builds, with runtime skip/ignore handled per test. The always-public `tls_gen` differs from the test-only pattern and may affect non-test builds.

Test signals: successful test compilation indicates every declared module resolves. Behavioral signals come from the individual module tests; this file’s direct signal is coverage reachability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/lib.rs -->
