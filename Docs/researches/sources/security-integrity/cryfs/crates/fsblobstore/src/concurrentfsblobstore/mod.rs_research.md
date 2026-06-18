# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/mod.rs

Purpose: Public module root for concurrent fsblobstore support.

Important APIs/types/functions: declares `blob`, `loaded_blobs`, and `store`, and re-exports `ConcurrentFsBlob`, `LoadedBlobGuard`, `RequestRemovalResult`, and `ConcurrentFsBlobStore`.

Control flow: no runtime behavior; it shapes the crate API.

State and persistence behavior: no state here. The exported store coordinates loaded blob state and delegates persistence to `fsblobstore`.

Dependencies and integration points: consumed by crate root `lib.rs` and higher-level filesystem code needing concurrent blob access.

Risks: re-exporting `LoadedBlobGuard` exposes a low-level cache concept; misuse can bypass higher-level invariants if used outside intended store paths.

Test signals: compile/API tests and downstream usage of `ConcurrentFsBlobStore` cover this module.
