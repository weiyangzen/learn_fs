# sources/storage-engines/rocksdb/db/blob/blob_file_cache.cc

## Purpose
Implements a typed cache for `BlobFileReader` objects so blob reads can share open file readers and coordinate refreshes for direct-write active blob files.

## Important APIs and Control Flow
`GetBlobFileReader` looks up a cache key derived from blob file number, returns a guarded handle on hit, otherwise locks a per-key stripe, double-checks, records `NO_FILE_OPENS`, creates a `BlobFileReader`, optionally retries footer-validation corruption with `skip_footer_validation`, inserts it with charge 1, releases ownership to cache, and returns a guard. `OpenBlobFileReaderUncached` opens without insertion. `InsertBlobFileReader` installs an uncached reader unless another thread already cached one. `RefreshBlobFileReader` compares cached and new reader file sizes; it preserves the larger observed size, otherwise erases/replaces under the stripe mutex. `Evict` erases a blob reader under lock.

## State, Dependencies, and Risks
State includes a `BasicTypedCacheInterface<BlobFileReader>`, 128 mutex stripes, immutable/file options, column family id, histogram, and IO tracer. Dependencies include `BlobFileReader::Create`, cache handle guards, statistics tickers, logging, and hash-derived cache keys. Risks include shared cache capacity failures, reader replacement races if file size is not a sufficient freshness proxy, and optional footer-skip retry for active/incomplete files. Tests cover cache hits, race double-checking, refresh preserving largest file size, missing-file errors, and strict-capacity failures.
