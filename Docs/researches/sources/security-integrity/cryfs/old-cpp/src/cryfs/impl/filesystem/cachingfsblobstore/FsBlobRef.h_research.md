# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 48 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CachingFsBlobStore`, `FsBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_FSBLOBREF_H`. Important declarations or call sites include `virtual ~FsBlobRef();`; `virtual const blockstore::BlockId &blockId() const = 0;`; `virtual fspp::num_bytes_t lstat_size() const = 0;`; `const blockstore::BlockId &parentPointer() const {`; `return _baseBlob->parentPointer();`; `void setParentPointer(const blockstore::BlockId &parentBlobId) {`; `return _baseBlob->setParentPointer(parentBlobId);`; `cpputils::unique_ref<fsblobstore::FsBlob> releaseBaseBlob() {`; `return std::move(_baseBlob);`; `FsBlobRef(cpputils::unique_ref<fsblobstore::FsBlob> baseBlob, cachingfsblobstore::CachingFsBlobStore *fsBlobStore): _fsBlobStor...`. CMake commands used here include `FsBlobRef`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cryfs/impl/filesystem/fsblobstore/FsBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `cryfs/impl/filesystem/fsblobstore/FsBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.
