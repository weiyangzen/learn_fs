# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/store.rs

Purpose: Defines `ConcurrentFsBlobStore`, a concurrency-safe wrapper around `FsBlobStore`.

Important APIs/types/functions: `new` wraps the base store and loaded-blob table in `AsyncDropArc`. Creation APIs create root, file, directory, and symlink blobs and insert them into `LoadedBlobs`. `load` deduplicates concurrent loads. `remove_by_id` coordinates cache-aware removal. `flush_if_cached`, `num_blocks`, space-estimation, and logical-block-size methods delegate to the underlying store.

Control flow: creating a non-root blob first creates through `FsBlobStore`, then inserts the new id as loaded. Loading calls `LoadedBlobs::get_loaded_or_insert_loading` with a cloned base store. Removing loops while another task is dropping the id. Flush checks the loaded cache first and locks the blob for direct flush; if absent, it asks lower layers to flush cached blocks.

State and persistence behavior: in-memory state is two shared async-drop arcs: the base store and loaded cache. Persistent state lives in the underlying blobstore. Async drop first drops loaded blobs, allowing dirty directory entries to write back, then drops the base store.

Dependencies and integration points: central bridge between `fsblobstore` and callers that need shared mutable access. Uses `FlushBehavior`, `ConcurrentFsBlob`, `LoadedBlobs`, and `cryfs_utils` async-drop helpers.

Risks: `expect("blob id is new")` assumes the base store always generates fresh ids. All blob operations are per-blob serialized, so a long operation under `with_lock` blocks other users of that blob. Root creation uses a loading slot to avoid races but returns only success/failure, not the root handle.

Test signals: useful tests should cover concurrent load deduplication, remove-vs-load races, flush of loaded and unloaded blobs, and drop ordering with dirty directory blobs.
