# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/guard.rs

Purpose: Defines `LoadedBlobGuard`, the RAII handle returned for one loaded `FsBlob` entry in the concurrent blob cache.

Important APIs/types/functions: `LoadedBlobGuard::new` wraps a `cryfs_concurrent_store::LoadedEntryGuard<BlobId, AsyncDropTokioMutex<FsBlob<B>>, Arc<anyhow::Error>>`. `blob_id` exposes the cache key. `with_lock` serializes mutable access to the underlying typed `FsBlob`. `remove` asks the concurrent store for an immediate drop and removes the blob from persistent storage through `FsBlob::remove`.

Control flow: callers get a guard from `LoadedBlobs`; operations run inside the per-blob async mutex. Removal loops because another task may already be dropping the same entry. When removal is accepted, this guard is async-dropped first so it no longer prevents exclusive removal, then the returned drop future is awaited.

State and persistence behavior: the guard itself owns no persistent data; it protects a cached `FsBlob` whose final removal deletes the backing blob. Async drop releases the loaded-entry guard and uses `InfallibleUnwrap` because the lower-level guard is expected not to fail.

Dependencies and integration points: integrates `cryfs_concurrent_store`, `AsyncDropTokioMutex`, `FsBlob`, `BlobId`, and `RemoveResult`. `ConcurrentFsBlob::remove` delegates to this type.

Risks: removal contains a panic for the logically impossible unloaded case while a guard is held. If the returned removal future is not driven, removal can stall. Errors are wrapped in `Arc<anyhow::Error>`, which preserves sharing but makes typed recovery harder.

Test signals: no local tests are present. Useful coverage would include concurrent readers plus removal, retry after `AlreadyDropping`, and ensuring `with_lock` excludes simultaneous mutation.
