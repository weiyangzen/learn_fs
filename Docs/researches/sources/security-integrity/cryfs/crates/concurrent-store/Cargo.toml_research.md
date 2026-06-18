<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml -->
# sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml

Purpose: crate manifest for `cryfs-concurrent-store`, the shared async loading/cache/drop coordination crate.

Important APIs/types/functions: declares the package metadata through workspace fields and exposes no binary targets. The code exports `ConcurrentStore`, `LoadedEntryGuard`, `Inserting`, `LoadingOrLoaded`, and `RequestImmediateDropResult` from `src/lib.rs`.

Control flow: build configuration is simple: default features are empty, and a `testutils` feature exists for test-only helpers exposed by dependent code.

State and persistence: no runtime persistence is configured here. The manifest controls dependency linkage and feature gates.

Dependencies/integration: depends on `anyhow`, `async-trait`, `futures`, `lockable`, `tokio`, `log`, `cryfs-utils`, and `cryfs-version`. These dependencies match the implementation's async drop guards, shared futures, mutex-held state machine, and cargo/git version assertion.

Risks/test signals: there are no dev-dependencies or local tests in this crate manifest. Behavioral confidence must come from downstream crate tests or future direct tests for cancellation, immediate drop, and waiter accounting.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml -->
