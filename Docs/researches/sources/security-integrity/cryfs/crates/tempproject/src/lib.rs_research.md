# sources/security-integrity/cryfs/crates/tempproject/src/lib.rs

Purpose: crate root and public API documentation for temporary Cargo project creation/build/run utilities.

Important APIs/types/functions: enables `#![forbid(unsafe_code)]` and `#![deny(missing_docs)]`; declares `builder` and `project`; re-exports `TempProjectBuilder`, `ProcessError`, and `TempProject`.

Control flow/state: no runtime logic beyond module loading. Documentation examples show creation, running, and error handling.

Dependencies/integration: makes the crate's ergonomic surface a small set of types from internal modules.

Risks: `deny(missing_docs)` means new public APIs must be documented. Docs claim build caching; actual `build_debug/build_release` methods recompute and only `run_*` reliably uses `OnceLock`.

Test signals: doc examples are `no_run`; behavioral tests live in `tests/simple.rs`.
