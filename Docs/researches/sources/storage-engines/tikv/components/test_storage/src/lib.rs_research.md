# Research: sources/storage-engines/tikv/components/test_storage/src/lib.rs

## sources/storage-engines/tikv/components/test_storage/src/lib.rs

Purpose: crate root for test storage helpers. It enables the unstable `box_patterns` feature required by error-pattern matches in assertion code, imports `tikv_util` macros, declares internal modules, and reexports all public helpers from `assert_storage`, `sync_storage`, and `util`.

There are no runtime functions in this file. Its API is the aggregated public surface of the crate: synchronous storage wrappers, assertion helpers, raft-engine macros, and utility constructors. Control flow is compile-time module wiring.

State and persistence are absent here, but the reexports expose helpers that create temporary engines, raft clusters, storage contexts, and GC workers. Dependencies are indirect through the submodules and `tikv_util` macros.

Risks are crate-wide: use of nightly-only `box_patterns` and macro import style means compiler/toolchain changes can break tests before runtime. Test signals are successful compilation of downstream tests that import `test_storage::*` rather than individual modules.
