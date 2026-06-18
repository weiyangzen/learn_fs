## sources/security-integrity/cryfs/crates/check/tests/common/mod.rs

Purpose: declares the shared test-support modules for the check integration tests.

Important APIs and functions: it exports `console`, `entry_helpers`, and `fixture` as public submodules. The crate-level `#![allow(dead_code)]` is intentional because parameterized test files consume different subsets of the shared helpers.

Control flow and state: no runtime logic or persistence exists here; it is compile-time module wiring for integration-test crates that declare `mod common`.

Dependencies and integration: each test file imports this module to access `FilesystemFixture`, `SomeBlobs`, blob creation helpers, and error expectation helpers. It centralizes common code without requiring a separate test-support crate.

Risks and test signals: dead-code allowance can hide truly stale helpers, but in this context it avoids noisy warnings from a deliberately broad fixture toolkit. Any missing module declaration would surface immediately as integration test compile failures.
