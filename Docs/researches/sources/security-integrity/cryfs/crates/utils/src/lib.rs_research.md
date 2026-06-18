# sources/security-integrity/cryfs/crates/utils/src/lib.rs

Purpose: root module for the `cryfs-utils` crate.

Important APIs/types/functions: exposes modules for async drop, exit handling, binary IO, concurrent tasks, containers, data, events, lazy reclaim, multi-receiver oneshot channels, mutex helpers, path utilities, peekable/periodic/progress/stream/threadpool/tmpfile, and test utilities under cfg. It invokes `cryfs_version::assert_cargo_version_equals_git_version!()`.

Control flow/state: no direct runtime flow beyond compile-time/module initialization and version assertion macro expansion.

Dependencies/integration: central import surface for all workspace utilities.

Risks: `forbid(unsafe_code)` and `deny(missing_docs)` are commented out, so unsafe and undocumented public APIs are currently allowed. Public module exposure has high semver impact.

Test signals: child modules provide tests; version assertion catches package metadata mismatches.
