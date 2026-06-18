<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go

## Purpose
This file defines `SharedChunkCacheManager`, a chunk-addressing helper for a cache that can be shared across gcsfuse mount instances. It computes stable chunk paths based on bucket, object name, generation, and chunk index, provides temp paths for atomic chunk writes, and applies include/exclude regex filtering.

## Important APIs and types
`NewSharedChunkCacheManager` stores cache directory, chunk size, permissions, config, and compiled regexes. `ShouldExcludeFromCache` applies include-then-exclude logic to `bucket/object` paths. `GenerateTmpPath` appends a random 16-hex-character temp suffix to a final chunk path. `GetChunkIndex`, `GetChunkSize`, `GetObjectDir`, `GetChunkPath`, `GetFilePerm`, and `GetDirPerm` expose path, sizing, and permissions. `computeObjectHash` SHA256-hashes length-prefixed bucket/object/generation fields.

## Control flow and state behavior
The manager itself does not persist data; it deterministically maps object identity to filesystem paths. Object directories are sharded by the first four hex digits of the SHA256 hash as `<cache>/<p1>/<p2>/<hash>`. Chunk files are named `<start>_<end>.bin` using configured fixed chunk size. Temp path generation uses `math/rand/v2.Uint64`, producing collision-resistant names but not cryptographic randomness.

## Dependencies and integration points
The manager depends on `cfg.FileCacheConfig`, regex compilation, `filepath`, SHA256/hex, file permissions, logging for invalid regex warnings, and GCS bucket/object metadata. It is designed for shared-cache code that can use mkdir/rename-style atomic operations, though those operations are not implemented in this file.

## Risks and edge cases
If `SharedCacheChunkSizeMb` is zero, chunk size becomes zero; tests document this current behavior, but callers must avoid division by zero in `GetChunkIndex`. Invalid regexes only warn and become nil filters, potentially caching more objects than intended. The hash uses generation, so overwrites naturally map to a new directory but require external cleanup for old generations.

## Test signals
`shared_chunk_cache_manager_test.go` verifies constructor fields, regex precedence, chunk index and size calculations, exact hash-derived paths, temp-path format and uniqueness over repeated calls, and permission getters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go -->
