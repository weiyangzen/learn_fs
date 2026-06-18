# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 58 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FileBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_FILEBLOBREF_H`. Important declarations or call sites include `_base(dynamic_cast<fsblobstore::FileBlob*>(baseBlob())) {`; `ASSERT(_base != nullptr, "We just initialized this with a pointer to FileBlob. Can't be something else now.");`; `void resize(fspp::num_bytes_t size) {`; `return _base->resize(size);`; `fspp::num_bytes_t size() const {`; `return _base->size();`; `fspp::num_bytes_t read(void *target, fspp::num_bytes_t offset, fspp::num_bytes_t count) const {`; `return _base->read(target, offset, count);`; `void write(const void *source, fspp::num_bytes_t offset, fspp::num_bytes_t count) {`; `return _base->write(source, offset, count);`. CMake commands used here include `FileBlobRef`, `_base`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/FileBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/FileBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.
