# sources/security-integrity/cryfs/crates/utils/src/async_drop/mod.rs

Purpose: module facade for async-drop utilities.

Important APIs/types/functions: re-exports `AsyncDrop`, `AsyncDropGuard`, `AsyncDropArc`, `AsyncDropTokioMutex`, `SyncDrop`, `AsyncDropHashMap`, `with_async_drop`, `flatten_async_drop`, `AsyncDropShared`, and `AsyncDropResult`.

Control flow/state: no runtime logic; establishes public API organization.

Dependencies/integration: downstream crates import most async cleanup helpers through `cryfs_utils::async_drop`.

Risks: adding a utility without re-exporting may hide it from intended users. Re-export names define semver-facing API.

Test signals: compile-time module wiring plus tests in child modules.
