# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/mod.rs

Purpose: module facade for generic handle utilities.

Important APIs: conditionally declares `handle_pool` and `handle_map` for FUSE-enabled builds, always declares `handle_with_generation` and `handle_trait`, and re-exports `HandlePool`, `HandleMap`, `HandleWithGeneration`, and `HandleTrait`.

Control flow and state: no runtime behavior. Feature gating keeps handle map/pool out when neither backend is built.

Dependencies and integration: imported by `common/mod.rs`, then re-exported through the crate root.

Risks and tests: public surface varies by feature flags, so downstream code must enable `fuser` or `fuse_mt` when using pool/map types.
