# sources/storage-engines/rocksdb/db/blob/blob_file_cache_test.cc

## Purpose
Tests `BlobFileCache` open/cache/refresh/error behavior using mock filesystem blob files.

## Important Test Flow
`WriteBlobFile` creates a valid blob log with one record and footer. `GetBlobFileReader` verifies first read opens and caches, second read reuses the same reader, and statistics show one open and no errors. `GetBlobFileReader_Race` uses a sync point to recursively open the same file between initial miss and lock acquisition, validating double-check behavior. `RefreshBlobFileReaderPrefersLargestObservedFileSize` creates an active blob file, opens stale and fresh uncached readers with footer-skip retry, refreshes cache with the larger observed size, and confirms a later stale refresh preserves the larger cached reader. Error tests cover missing blob file I/O error and zero-capacity strict cache memory-limit failure.

## Dependencies, Risks, and Test Signals
The tests depend on mock env, blob log writer, file naming, cache implementation, statistics, and sync points. They directly signal concurrency and active-file refresh correctness. They do not cover explicit `Evict` or `InsertBlobFileReader` separately.
