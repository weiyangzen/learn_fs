# sources/security-integrity/cryfs/crates/tempproject/tests/simple.rs

Purpose: integration tests for `tempproject` covering success, build-time failure, runtime failure, debug/release profiles, and builder edge cases.

Important APIs/types/functions: fixture constructors create successful, compile-failing, and runtime-failing projects. Expectation helpers validate `build_debug`, `build_release`, `run_debug`, and `run_release` behavior.

Control flow: tests are grouped by operation path: build only, run only, and build then run for both debug and release. Edge cases assert panics when required builder fields are absent.

State/persistence: every fixture creates a temp Cargo project and build artifacts under its temp directory. Cargo execution is real, not mocked.

Dependencies/integration: uses `assert_cmd::Command`, `indoc`, `predicates`, and public crate APIs.

Risks: tests depend on a working Rust toolchain and may be slower/flakier than pure unit tests. Compiler diagnostic assertion for `nonexisting_func` is somewhat tied to rustc wording.

Test signals: strong coverage of the crate's intended workflow, but no direct test that repeated `build_*` calls avoid rebuilding.
