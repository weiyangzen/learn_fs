# sources/storage-engines/rocksdb/db/blob/blob_file_cache.h

## Purpose
Declares `BlobFileCache`, the cache facade for opening, caching, refreshing, and evicting blob file readers.

## Important APIs and State
`GetBlobFileReader` returns a cached reader, opening and caching on miss. `OpenBlobFileReaderUncached` opens without cache insertion. `InsertBlobFileReader` transfers a unique reader into the cache unless one already exists. `RefreshBlobFileReader` replaces an existing reader only when the new reader has seen a larger file size. `Evict` removes obsolete file readers. `GetHelper` exposes the typed cache helper. Members include the typed cache interface, striped mutexes, immutable/file options, column family id, read histogram, and IO tracer.

## Dependencies, Risks, and Integration
It depends on `typed_cache.h`, `BlobFileReader`, and RocksDB cache APIs. State is in the shared cache and mutex stripes, not persisted on disk. Risks include requiring caller-provided `CacheHandleGuard` emptiness, ownership transfer via raw pointer release, and shared cache collisions/capacity with table cache. Integration points are blob reads, direct-write blob fallback, file obsoletion, and tests in `blob_file_cache_test.cc`.
