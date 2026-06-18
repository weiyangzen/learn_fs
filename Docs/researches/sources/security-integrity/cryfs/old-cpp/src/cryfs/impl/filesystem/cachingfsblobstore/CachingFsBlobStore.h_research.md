# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 115 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CachingFsBlobStore`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_CACHINGFSBLOBSTORE_H`. Important declarations or call sites include `CachingFsBlobStore(cpputils::unique_ref<fsblobstore::FsBlobStore> baseBlobStore);`; `~CachingFsBlobStore();`; `cpputils::unique_ref<FileBlobRef> createFileBlob(const blockstore::BlockId &parent);`; `cpputils::unique_ref<DirBlobRef> createDirBlob(const blockstore::BlockId &parent);`; `cpputils::unique_ref<SymlinkBlobRef> createSymlinkBlob(const boost::filesystem::path &target, const blockstore::BlockId &parent);`; `boost::optional<cpputils::unique_ref<FsBlobRef>> load(const blockstore::BlockId &blockId);`; `void remove(cpputils::unique_ref<FsBlobRef> blob);`; `void remove(const blockstore::BlockId &blockId);`; `uint64_t virtualBlocksizeBytes() const;`; `uint64_t numBlocks() const;`. CMake commands used here include `CachingFsBlobStore`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `remove`. Primary includes/dependencies visible in the file include `cpp-utils/pointer/unique_ref.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`, `blockstore/implementations/caching/cache/Cache.h`, `FileBlobRef.h`, `DirBlobRef.h`, `SymlinkBlobRef.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `cpp-utils/pointer/unique_ref.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`, `blockstore/implementations/caching/cache/Cache.h`, `FileBlobRef.h`, `DirBlobRef.h`, `SymlinkBlobRef.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.
