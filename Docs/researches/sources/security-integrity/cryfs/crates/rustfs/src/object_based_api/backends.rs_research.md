# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/backends.rs

Purpose: abstracts mounting an object-based filesystem through either supported backend.

Important APIs: `RustfsBackend` trait with associated `BackgroundSession`, `mount`, and `spawn_mount`; feature-gated `RustfsFuserBackend` and `RustfsFusemtBackend`; public re-exports of `fuser::{Config, MountOption, SessionACL}`.

Control flow and state: backend impls wrap a `Device` constructor in the appropriate adapter. Fuser uses `ObjectBasedFsAdapterLL`; fuse-mt uses the path-based `ObjectBasedFsAdapter`. Both delegate to backend-specific mount/spawn functions and return `RunningFilesystem` for spawned mounts.

Dependencies and integration: connects object API, backend module, `RunningFilesystem`, Tokio runtime handles, and cancellation triggers.

Risks and tests: behavior diverges by backend because fuser and fuse-mt use different adapter layers. Generic bounds are broad (`Send`, `Sync`, `Debug`, `'static`) and TODOs question whether all are necessary.
