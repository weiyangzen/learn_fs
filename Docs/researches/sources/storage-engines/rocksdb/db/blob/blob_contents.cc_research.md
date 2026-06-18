# sources/storage-engines/rocksdb/db/blob/blob_contents.cc

## Purpose
Implements memory accounting for cached uncompressed blob values.

## Important APIs and Control Flow
`BlobContents::ApproximateMemoryUsage` adds allocation memory if `allocation_` exists. If a custom `MemoryAllocator` is attached to the deleter, it asks `allocator->UsableSize`; otherwise it uses `malloc_usable_size` when available or `data_.size()` as a fallback. It also accounts for the `BlobContents` object itself using `malloc_usable_size(this)` when available or `sizeof(*this)`.

## State, Dependencies, and Risks
The method depends on `CacheAllocationPtr`, allocator deleter state, and `ROCKSDB_MALLOC_USABLE_SIZE`. It persists no data, but it determines cache charge estimates for blob values. Risks are platform-dependent allocator reporting, `const_cast` use for `malloc_usable_size`, and fallback undercounting/overcounting. It integrates with typed cache insertion through `BlobContentsCreator`.
