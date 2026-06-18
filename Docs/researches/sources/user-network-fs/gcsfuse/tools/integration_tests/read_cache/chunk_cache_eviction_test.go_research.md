# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_eviction_test.go

Purpose: Tests LRU-like eviction for experimental chunk cache under a constrained cache size.

Important APIs/types/functions: `chunkCacheEvictionTest` uses common suite lifecycle. `TestEviction` creates two 20 MiB files, reads file 1 fully, file 2 fully, then reads file 1 again, and validates structured logs plus aggregate chunk download ranges.

Control flow: the first full read downloads two 10 MiB chunks for file 1. Reading file 2 forces eviction of file 1 when inserting file 2. Reading file 1 again forces file 2 eviction and redownloads file 1's first chunk. The test aggregates `ChunkCacheDownloads` from all job logs and compares expected ranges.

State/persistence: Cache size is 15 MiB per setup config, so each 20 MiB file exceeds capacity and eviction occurs on insertion. Content validation is skipped in `validateDownloads` because ranges span multiple files.

Dependencies/integration: Uses internal cache data/util types, read-cache helpers, log parser, and storage setup.

Risks/test signals: Expected ranges are value-only and not tied to object name in final comparison. Passing signals chunk-cache eviction and redownload behavior under capacity pressure.
