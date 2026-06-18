# sources/security-integrity/cryfs/crates/tempproject/Cargo.toml

Purpose: manifest for the `tempproject` crate, a workspace utility for creating temporary Cargo projects in tests.

Important APIs/types/functions: declares package metadata inherited from the workspace and dependencies on `anyhow`, `assert_cmd`, `is_executable`, `tempfile`, and `thiserror`. Dev dependencies are `indoc` and `predicates`.

Control flow/state: no runtime code, but dependency choices define the crate behavior: temp directories, process execution/assertion, executable discovery, and structured error derivation.

Dependencies/integration: participates in the workspace with shared version/edition/rust-version metadata. It is likely used by integration tests that need to compile generated Rust crates.

Risks: because it shells out to Cargo, workspace dependency resolution and environment `CARGO` path matter. `is_executable` behavior is platform-sensitive.

Test signals: crate tests in `tests/simple.rs` exercise build/run/error behavior.
