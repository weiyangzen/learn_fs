# sources/object-store/rustfs/crates/e2e_test/src/policy/mod.rs

Purpose: module root for policy-specific RustFS E2E tests focused on AWS IAM policy variable expansion.

Important APIs/types/functions: declares private modules `policy_variables_test`, `test_env`, and `test_runner`. It exposes no public API from this root.

Control flow: Rust test discovery compiles the variable tests and the ignored runner harness through this module. The actual test control flow lives in the child files.

State and persistence behavior: none locally. Child modules create users, policies, buckets, and cleanup state against a RustFS admin/S3 endpoint.

Dependencies and integration points: integrates the policy test namespace into the e2e crate. The private module layout keeps helpers scoped to policy tests.

Risks: low; accidental removal of a module declaration would silently drop its tests from the crate.

Test signals: module discovery only; substantive signals are in `policy_variables_test.rs` and `test_runner.rs`.
