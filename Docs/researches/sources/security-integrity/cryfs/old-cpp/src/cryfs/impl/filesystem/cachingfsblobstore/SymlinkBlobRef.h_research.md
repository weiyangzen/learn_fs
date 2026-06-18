# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 42 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SymlinkBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_SYMLINKBLOBREF_H`. Important declarations or call sites include `_base(dynamic_cast<fsblobstore::SymlinkBlob*>(baseBlob())) {`; `ASSERT(_base != nullptr, "We just initialized this with a pointer to SymlinkBlob. Can't be something else now.");`; `const boost::filesystem::path &target() const {`; `return _base->target();`; `const blockstore::BlockId &blockId() const override {`; `return _base->blockId();`; `fspp::num_bytes_t lstat_size() const override {`; `return _base->lstat_size();`; `DISALLOW_COPY_AND_ASSIGN(SymlinkBlobRef);`. CMake commands used here include `SymlinkBlobRef`, `_base`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/SymlinkBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/SymlinkBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.
