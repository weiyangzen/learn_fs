# sources/security-integrity/cryfs/crates/rustfs/src/backend/mod.rs

Purpose: Backend module root for rustfs.

Important APIs/types/functions: declares `running_filesystem`, re-exports `BackgroundSession` and generic `RunningFilesystem`, and conditionally exposes `fuse_mt` and `fuser` backend modules according to features.

Control flow: none directly; feature gates determine compiled backend surface.

State and persistence behavior: no state here. `RunningFilesystem` owns background sessions and unmount behavior in its own module.

Dependencies and integration points: central import point for example binaries and downstream users selecting a backend.

Risks: feature-gated exports mean downstream code must align Cargo features with imports. Both backends share type names, so callers should import through the chosen submodule.

Test signals: build matrix for default, `--no-default-features`, `--features fuser`, and `--features fuse_mt`.
