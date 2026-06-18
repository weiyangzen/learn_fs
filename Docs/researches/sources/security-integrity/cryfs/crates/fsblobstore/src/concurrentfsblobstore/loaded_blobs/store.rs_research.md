# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/store.rs

Purpose: Implements `LoadedBlobs`, the process-local cache and synchronization table for typed `FsBlob` instances.

Important APIs/types/functions: `new` creates a `ConcurrentStore<BlobId, AsyncDropTokioMutex<FsBlob<B>>, Arc<anyhow::Error>>`. `try_insert_loading` registers an in-flight load/create future. `try_insert_loaded` inserts a newly created blob. `get_loaded_or_insert_loading` deduplicates concurrent loads. `get_if_loading_or_loaded` probes the cache. `request_removal` coordinates safe removal and returns `RequestRemovalResult`.

Control flow: loading functions transform `FsBlob` into `AsyncDropTokioMutex<FsBlob>` so all users share one mutable instance. A caller that wins a load waits until the insertion completes. Removal uses `request_immediate_drop`; if the blob is loaded it unwraps the mutex and calls `FsBlob::remove`, otherwise it removes directly from `FsBlobStore` while the concurrent-store drop slot blocks new loads.

State and persistence behavior: cache state is in memory; persistent effects are delegated to `FsBlobStore::remove_by_id` or `FsBlob::remove`. Async drop drops all cached entries, which can trigger directory writeback through `FsBlob` async drop.

Dependencies and integration points: depends on `cryfs_concurrent_store`, `AsyncDropArc`, `AsyncDropTokioMutex`, `FsBlobStore`, and `RemoveResult`. `ConcurrentFsBlobStore` owns one `LoadedBlobs`.

Risks: the caller must poll `RequestRemovalResult::RemovalRequested.on_removed` to completion or the entry can remain blocked. The comments note `Arc<anyhow::Error>` as a coarse error channel and possible hash-performance concerns for random blob ids.

Test signals: targeted tests should assert load deduplication, direct removal of unloaded blobs, loaded removal waiting for guards, and retry behavior when an entry is already dropping.
