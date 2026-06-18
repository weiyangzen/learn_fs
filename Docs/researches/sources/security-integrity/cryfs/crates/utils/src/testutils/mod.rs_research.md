# sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs

Purpose: Exposes the test utility submodules from the `cryfs_utils::testutils` namespace.

Important APIs and types: It declares `pub mod asserts;`, `pub mod data_fixture;`, and `pub mod static_drop;`.

Control flow: There is no runtime control flow; this is a module wiring file.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Downstream tests use this module to reach custom assertions, deterministic data fixtures, and static cleanup helpers when the crate's `testutils` feature is enabled.

Risks: Any module added here becomes part of the testutils public module layout. Removing or renaming exports would break tests or external users that depend on the feature.

Test signals: This file has no local tests; coverage comes from each exported module and integration tests that import through `cryfs_utils::testutils`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs` completely for this pass (3 lines, 60 bytes).
