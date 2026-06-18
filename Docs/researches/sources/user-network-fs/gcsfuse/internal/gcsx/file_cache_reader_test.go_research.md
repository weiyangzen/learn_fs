## sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader_test.go

Purpose: broad unit coverage for `FileCacheReader` across non-zonal, zonal, and rapid/Pirlo bucket types.

Important APIs and fixtures: `fileCacheReaderTest`, suite variants by bucket type, temp cache directories, `cacheHandler`, mock bucket readers, `mockNewReaderWithHandleCallForTestBucket`, and helper waits for download jobs. It uses fake readers and generated random data to verify actual buffer contents.

Control flow and behavior covered: constructor fields, fallback when cache handler is nil, oversized object cache exclusion, EOF at or beyond object size, cache hits, sequential read reuse, random read behavior with `cacheFileForRangeRead` true/false, transitions from sequential to random, invalid job and invalid file handle recovery, deleted cache file behavior, failed job restart, negative/beyond-size offsets, and destroy.

State/persistence signals: tests observe job-manager state, local cache file deletion, cache handle reuse, invalidation by `InvalidateCache`, and Linux semantics where an open file handle can continue serving data after unlink. Unfinalized object scenarios verify behavior when object size grows relative to cached size.

Dependencies/integration: uses cache file package, cache job manager, storage mocks, fake readers, metrics/tracing noop handles, and `testify/suite`.

Risks/test signals: strong coverage for cache lifecycle and locking, including concurrent `ReadAt` and concurrent `ReadAt` plus `Destroy` without panic. Tests remain local/fake and do not validate filesystem differences outside Linux-style unlink semantics assumed in comments.
