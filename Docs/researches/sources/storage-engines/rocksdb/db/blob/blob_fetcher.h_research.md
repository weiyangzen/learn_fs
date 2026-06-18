# sources/storage-engines/rocksdb/db/blob/blob_fetcher.h

## Purpose
Declares `BlobFetcher`, a thin read helper that abstracts whether a blob value should be read through a manifest-visible `Version` or through a direct-write fallback path.

## Important APIs and State
The constructor stores a `const Version*`, `ReadOptions`, optional `BlobFileCache*`, and `allow_write_path_fallback_`. Two `FetchBlob` overloads accept either a serialized blob-index slice or a decoded `BlobIndex`, plus prefetch buffer, output `PinnableSlice`, and optional bytes-read counter.

## Dependencies, Risks, and Integration
The header forward-declares blob/read support types and includes options/status. It persists no data itself but participates in read-path state resolution. Risks include caller-supplied pointer lifetime for `Version` and `BlobFileCache`, and ambiguity if fallback is enabled without the necessary cache. Integration points are DB read paths that encounter blob indexes and need to materialize values.
