# sources/sync-backup/casync/src/cacache.c

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.c -->
## sources/sync-backup/casync/src/cacache.c

Purpose: `cacache.c` implements `CaCache`, a reference-counted lookup cache that maps a source `CaLocation` to a chunk ID and origin chain. It accelerates repeated chunk generation by avoiding rehashing unchanged source locations.

Important APIs and functions: `ca_cache_new/ref/unref` manage lifetime. `ca_cache_set_digest_type`, `ca_cache_set_fd`, and `ca_cache_set_path` configure the cache before use. `ca_cache_get` reads a cache entry and reconstructs `CaOrigin`. `ca_cache_put` writes an origin-to-chunk mapping. `ca_cache_remove` deletes a mapping. Internally `ca_cache_open` lazily creates/opens the cache directory and marks it `FS_NODUMP_FL`.

Control flow: cache keys are derived from the first location via `ca_location_id_make` and formatted through `ca_chunk_id_format_path` with `.cachi` suffix. `get` accepts two on-disk formats: symlink targets for single-location origins, and regular files containing a binary chunk ID followed by NUL-terminated location strings. It validates that cached locations include size and mtime and that the first origin item matches the lookup location. `put` prefers a symlink for a single origin item, otherwise writes a temporary regular file and atomically renames it.

State and persistence: persistent state lives in the cache directory as sharded `.cachi` entries. The object stores fd/path/digest state in memory. Writes are immutable-ish: existing entries cause a no-op success result.

Dependencies and integration points: depends on `cachunkid`, `calocation`, `caorigin`, `cadigest`, `realloc-buffer`, `chattr`, and utility cleanup helpers. It integrates with chunk generation and matching paths that can use cached origins.

Risks: cache correctness depends on location metadata, especially mtime and feature flags. Corrupt or truncated entries return `-EINVAL`. Symlink target length can force fallback to regular files. `ca_cache_set_fd` takes ownership-like responsibility for the fd and closes it on unref; callers must not also close it unexpectedly. Cache entries are redundant but stale entries can reduce performance or produce validation failures.

Test signals: unit tests should cover missing cache path, symlink entries, regular file entries, stale metadata mismatch, corrupt/truncated data, duplicate put idempotence, and remove cleanup of empty shard directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.c -->
