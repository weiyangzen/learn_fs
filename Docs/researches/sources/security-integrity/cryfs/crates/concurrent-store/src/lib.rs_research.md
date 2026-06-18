<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs

Purpose: crate root for the unsafe-free concurrent store abstraction.

Important APIs/types/functions: forbids unsafe code, allows private intra-doc links, declares internal modules, and re-exports `LoadedEntryGuard`, `Inserting`, `LoadingOrLoaded`, `ConcurrentStore`, and `RequestImmediateDropResult`.

Control flow: no runtime flow beyond module wiring. The public surface is intentionally small and channels callers through RAII handles.

State and persistence: state lives in `store.rs` and entry modules. The root adds no persistence behavior.

Dependencies/integration: invokes `cryfs_version::assert_cargo_version_equals_git_version!()` to enforce version consistency between Cargo metadata and git-derived versioning.

Risks/test signals: missing-docs is a TODO, so public APIs may be underdocumented for downstream users. Feature `testutils` is configured in Cargo but not surfaced here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs -->
