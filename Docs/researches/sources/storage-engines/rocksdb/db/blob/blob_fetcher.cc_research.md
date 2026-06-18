# sources/storage-engines/rocksdb/db/blob/blob_fetcher.cc

## Purpose
Implements blob retrieval routing for decoded and encoded blob indexes.

## Important APIs and Control Flow
`FetchBlob(user_key, blob_index_slice, ...)` decodes a `BlobIndex` from the provided slice, then delegates to the overload taking `const BlobIndex&`. The second overload either calls `version_->GetBlob` when write-path fallback is disabled, or calls `BlobFilePartitionManager::ResolveBlobDirectWriteIndex` when fallback is allowed. The fallback path can resolve direct-write blob files not yet visible in the manifest using the optional `BlobFileCache`.

## State, Dependencies, and Risks
The class stores `Version*`, copied `ReadOptions`, optional `BlobFileCache*`, and a fallback flag. Dependencies include `BlobIndex`, `Version`, `BlobFilePartitionManager`, `FilePrefetchBuffer`, and `PinnableSlice`. Risks include requiring non-null `version_` in normal path, handling decode corruption, and ensuring fallback does not bypass visibility/consistency constraints. Test coverage is likely through blob read and write-path direct-write tests.
