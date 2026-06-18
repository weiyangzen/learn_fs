# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 49 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `optional<unique_ref<FsBlobRef>> CachingFsBlobStore::load(const BlockId &blockId) {`; `auto fromCache = _cache.pop(blockId);`; `if (fromCache != none) {`; `return _makeRef(std::move(*fromCache));`; `auto fromBaseStore = _baseBlobStore->load(blockId);`; `if (fromBaseStore != none) {`; `return _makeRef(std::move(*fromBaseStore));`; `unique_ref<FsBlobRef> CachingFsBlobStore::_makeRef(unique_ref<FsBlob> baseBlob) {`; `auto fileBlob = dynamic_pointer_move<FileBlob>(baseBlob);`; `if (fileBlob != none) {`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `CachingFsBlobStore.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `CachingFsBlobStore.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- `_makeRef` uses `dynamic_pointer_move` to wrap base file, directory, or symlink blobs in the matching cached reference type.
