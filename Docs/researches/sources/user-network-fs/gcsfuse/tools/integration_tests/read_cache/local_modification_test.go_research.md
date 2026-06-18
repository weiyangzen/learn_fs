# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/local_modification_test.go

Purpose: Tests cache behavior after a file is modified locally through the gcsfuse mount.

Important APIs/types/functions: `localModificationTest` uses common suite setup. `TestReadAfterLocalGCSFuseWriteIsCacheMiss` creates a mounted file, reads it to populate cache, appends random data through the mount, then validates behavior with separate branches for zonal and non-zonal buckets.

Control flow: non-zonal path expects the second full read after append to miss cache and read `fileSize + smallContentSize`, with structured logs showing miss and increased chunk count. Zonal path expects unfinalized-object semantics: no new download job for appends, cache file remains original size, cache size remains within limit, and the second log is treated as cache hit while fallback serves newer bytes.

State/persistence: The test mutates the object through the mount, so local write state and cache generation tracking are central. Cache file size is inspected directly for zonal behavior.

Dependencies/integration: Uses read-cache helpers, storage client, operations random data and append helpers, setup bucket-type check, and structured read logs.

Risks/test signals: The zonal branch encodes specialized behavior for unfinalized objects and may diverge from non-zonal assumptions. Passing signals local writes invalidate or bypass stale cache appropriately.
