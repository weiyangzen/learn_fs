# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/blob.rs

## Purpose
This file defines `ConcurrentFsBlob`, a concurrency-safe wrapper around a loaded filesystem blob guard. It exposes blob identity, blob type lookup, locked mutable access to the underlying `FsBlob`, explicit removal, and async-drop cleanup.

## Important APIs, Types, and Functions
`ConcurrentFsBlob<B>` is generic over a backend `B` implementing `BlobStore + AsyncDrop<Error = anyhow::Error> + Debug + Send + 'static`, with a concrete blob that is `Send + AsyncDrop`. Its single field is `blob: AsyncDropGuard<LoadedBlobGuard<B>>`.

Important methods are `new`, `blob_id`, `blob_type`, `with_lock`, and associated async `remove`. It implements `AsyncDrop` by delegating to the wrapped loaded blob guard.

## Control Flow
`new` wraps a `LoadedBlobGuard` in `ConcurrentFsBlob` and returns it inside `AsyncDropGuard`. `blob_id` delegates directly. `blob_type` acquires the internal lock and asks the underlying `FsBlob` for its type. `with_lock` is a generic async critical-section helper that passes mutable `FsBlob<B>` access to the caller. `remove` consumes an `AsyncDropGuard<Self>`, extracts the inner wrapper without running its drop, and delegates removal to `LoadedBlobGuard::remove`.

## State and Persistence Behavior
The wrapper coordinates access to a loaded blob and ensures async cleanup is performed when dropped. Mutating operations must go through `with_lock`, preserving serialized access to the underlying `FsBlob`. `remove` is a destructive persistence operation returning `RemoveResult` or shared `Arc<anyhow::Error>`, and it intentionally consumes the guard to avoid later double-drop/double-remove behavior.

## Dependencies and Integration Points
The file depends on `cryfs_blobstore::{BlobId, BlobStore, RemoveResult}`, `cryfs_utils::async_drop::{AsyncDrop, AsyncDropGuard}`, `LoadedBlobGuard`, and `BlobType`. It is part of `concurrentfsblobstore` and bridges public concurrent blob handles to the lower fsblobstore implementation.

## Risks and Notes
The most important risk is `unsafe_into_inner_dont_drop` in `remove`: correctness depends on `LoadedBlobGuard::remove` taking over all cleanup that async drop would otherwise perform. `blob_type` locks instead of caching by design because it is rare; this avoids stale cached metadata but adds lock overhead. Error sharing via `Arc<anyhow::Error>` suggests removal failures may need to be propagated to multiple owners.

## Test Signals
Relevant tests should verify drop delegation, lock serialization, blob ID/type access, successful remove, remove failure propagation, and absence of double cleanup after `remove` consumes the guard.
