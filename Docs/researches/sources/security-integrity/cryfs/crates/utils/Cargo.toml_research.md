# sources/security-integrity/cryfs/crates/utils/Cargo.toml

Purpose: manifest for `cryfs-utils`, a shared utility crate used across the CryFS Rust workspace.

Important APIs/types/functions: declares dependencies for async traits, binary serialization (`binrw`), version checks, derivations, futures/tokio, progress/logging, synchronization, random/hex utilities, and optional test utilities. Feature `testutils` enables optional `divrem` and `dtor`; criterion benchmark `path` is registered.

Control flow/state: no runtime code, but feature flags gate test-only APIs such as async-drop map iter/drain and binary helpers.

Dependencies/integration: central workspace crate. `cryfs-version` is a path dependency used by `lib.rs` to assert Cargo/git version alignment.

Risks: utility crates tend to be high blast-radius. Optional dependencies must remain aligned with feature-gated code paths. Tokio features are broad enough for filesystem/time/runtime use.

Test signals: many modules include unit tests; `benches/path.rs` benchmarks path joining.
