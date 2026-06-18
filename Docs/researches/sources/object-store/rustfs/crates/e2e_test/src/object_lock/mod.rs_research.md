# sources/object-store/rustfs/crates/e2e_test/src/object_lock/mod.rs

Purpose: module root for Object Lock E2E tests. It documents the suite scope and wires the helper module plus concrete test module into the crate.

Important APIs/types/functions: exports `pub mod common` for shared helper access and declares private `mod object_lock_test` for the test bodies. There are no runtime functions or types in this file.

Control flow: Rust's test harness compiles the nested modules; `object_lock_test.rs` contains the `#[tokio::test]` entries, while `common.rs` provides shared setup and S3 operations.

State and persistence behavior: none locally. State is created by the child modules in RustFS temp directories and S3 buckets.

Dependencies and integration points: integrates the Object Lock test namespace into the e2e crate. The public `common` visibility allows sibling tests or future modules to reuse Object Lock helpers.

Risks: very low. Any missing module declaration would remove tests from compilation. The private `object_lock_test` module keeps test bodies scoped to this module.

Test signals: test discovery signal only; the concrete signals are in `object_lock_test.rs`.
