# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/mod.rs

Purpose: `FsBlobStore` wraps a raw `BlobStore` and exposes typed filesystem blobs.

Important APIs/types/functions: `new`, create root/file/dir/symlink blob, `load`, `num_blocks`, space and logical-block-size queries, `remove_by_id`, `into_inner_blobstore`, test-only cache clearing, `flush_if_cached`, and `FlushBehavior`.

Control flow: create methods call the typed blob constructors and optionally flush immediately. `load` asks the raw blobstore for a blob and parses it into `FsBlob`. `remove_by_id` and flush/cache methods delegate to the underlying store.

State and persistence behavior: owns an `AsyncDropGuard<B>` raw store. Typed creation writes fsblob headers and data into the raw store. `FlushBehavior::DontFlush` allows batching but creates durability windows.

Dependencies and integration points: used directly by non-concurrent callers and wrapped by `ConcurrentFsBlobStore` for shared access. Re-exports most typed blob API.

Risks: `num_blocks` calls `blobstore.num_nodes()`, so naming may be confusing depending on lower-store semantics. Root creation errors if the id exists. No parent-chain validation occurs on load.

Test signals: important tests include create/load/remove for all blob types, flush behavior, invalid blob parse, root id collision, and cache flushing.
