# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/mod.rs

Purpose: Module facade for the loaded-blob cache internals.

Important APIs/types/functions: declares private `guard` and `store` modules, re-exporting `LoadedBlobGuard`, `LoadedBlobs`, and `RequestRemovalResult`.

Control flow: no runtime flow lives here. Its role is to narrow the public surface that `concurrentfsblobstore` exposes.

State and persistence behavior: no state. State lives in `LoadedBlobs` and `LoadedBlobGuard`.

Dependencies and integration points: imported by `concurrentfsblobstore/mod.rs`, `concurrentfsblobstore/blob.rs`, and `concurrentfsblobstore/store.rs`.

Risks: facade drift is the main risk; hiding internals is useful because removal/load coordination must stay centralized.

Test signals: build coverage is the signal. Any re-export change affects the concurrent blob store public API.
