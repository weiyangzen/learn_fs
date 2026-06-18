# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mod.rs

Purpose: Public facade for the fuser backend.

Important APIs/types/functions: declares private `backend_adapter` and `mount`, re-exports `mount` and `spawn_mount`, re-exports `fuser::{Config, MountOption, SessionACL}`, and defines backend-specific `RunningFilesystem`.

Control flow: none directly.

State and persistence behavior: no state; runtime session state is in `RunningFilesystem` returned by mount functions.

Dependencies and integration points: primary backend used by examples and tests for low-level rustfs filesystems.

Risks: re-exporting fuser config types couples public API to fuser 0.17. Backend behavior depends on feature selection in Cargo.

Test signals: default-feature build and fuser mount tests.
