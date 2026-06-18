# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mod.rs

Purpose: Public facade for the legacy `fuse_mt` backend.

Important APIs/types/functions: declares private `backend_adapter` and `mount`, re-exports `mount` and `spawn_mount`, re-exports shared fuser config/mount option/session ACL types, and defines backend-specific `RunningFilesystem`.

Control flow: none directly.

State and persistence behavior: no state; mounted sessions are returned by `mount.rs`.

Dependencies and integration points: only compiled with the `fuse_mt` feature; lets users mount a high-level `AsyncFilesystem`.

Risks: the backend depends on a compatibility bridge to fuser 0.16. API users should prefer the newer fuser backend where possible, matching comments in the adapter.

Test signals: feature-gated build and mount smoke tests.
