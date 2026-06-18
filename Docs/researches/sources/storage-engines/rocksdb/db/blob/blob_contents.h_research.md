# sources/storage-engines/rocksdb/db/blob/blob_contents.h

## Purpose
Declares `BlobContents`, the in-memory representation of a single uncompressed value read from a blob file, and its cache creation context.

## Important APIs and Types
`BlobContents` owns a `CacheAllocationPtr` and exposes a `Slice` over the allocated bytes. It is moveable but not copyable, provides `data()`, `size()`, `ApproximateMemoryUsage()`, and `ContentSlice()` for `FullTypedCacheInterface`. Its cache role is `CacheEntryRole::kBlobValue`. `BlobContentsCreator::Create` copies a saved slice into cache allocation, constructs `BlobContents`, and returns the approximate memory charge.

## State, Dependencies, and Risks
The persisted value for cache serialization is the content slice; object lifetime is tied to allocation ownership. Dependencies include memory allocator helpers, advanced cache interfaces, slices, and compression type signatures. Risks include cache charge accuracy and assuming the input slice already represents uncompressed blob contents. Integration points are blob cache reads and typed secondary-cache-compatible cache insertion.
