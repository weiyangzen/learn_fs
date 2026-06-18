# sources/security-integrity/cryfs/crates/fsblobstore/src/utils/mod.rs

Purpose: Utility module root for fsblobstore.

Important APIs/types/functions: exposes `fs_types`.

Control flow: none.

State and persistence behavior: none directly; `fs_types` values are serialized in directory entries.

Dependencies and integration points: imported by crate root and fsblob modules for uid/gid/mode support.

Risks: minimal. Re-export changes can affect downstream code paths that import utility types through this module.

Test signals: compile coverage plus `fs_types` tests.
