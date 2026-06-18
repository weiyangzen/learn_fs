# sources/sync-backup/git-lfs/locking/locks.go

Purpose: implements the high-level Git LFS locking client that commands use to create, remove, search, verify, cache, and apply local filesystem policy for locks.

Important APIs/types/functions: `LockCacher`, `Client`, `NewClient`, `SetupFileCache`, `Close`, `LockFile`, `UnlockFile`, `UnlockFileById`, `Lock`, `SearchLocks`, `SearchLocksVerifiable`, `searchLocalLocks`, `searchRemoteLocks`, `lockIdFromPath`, `IsFileLockedByCurrentCommitter`, `EncodeLocks`, `EncodeLocksVerifiable`, and `nilLockCacher`. `ErrNoMatchingLocks` and `ErrLockAmbiguous` are the main resolution errors.

Control flow: `NewClient` wires a generic HTTP/SSH-capable `lockClient`, config, local paths, and a no-op cache. `SetupFileCache` swaps in an on-disk lock cache and establishes a separate JSON cache directory. Lock and unlock calls send ref-aware API requests, translate server messages into user errors, update local cache state, and toggle local write permissions when required. Search either reads local cache, reads JSON cache, or pages the remote endpoint and optionally writes unfiltered unlimited results back to cache. Verifiable search clears the cache, pages `/locks/verify`, partitions ours/theirs, and writes a verifiable cache when unlimited.

State/persistence behavior: persistent state lives in `lockcache.db` via `LockCacher` and in JSON cache files under `<cacheDir>/locks/<refspec>/{remote,verifiable}`. File writability is also stateful: locked files are made writable after lock acquisition, and unlocked lockable files can be made read-only.

Dependencies/integration: depends on config paths, `git.Ref` refspecs, `lfsapi` clients, `filepathfilter` lockability helpers elsewhere in the package, `tools` filesystem helpers, `kv` storage registration, and `tracerx` request-id tracing.

Risks: `RemoteRef` is dereferenced in several paths and must be set by callers. Cache reads reject filters/limits, so callers must avoid treating cached search as a full query API. Cache directory names include refspecs, which can contain slashes and therefore intentionally form nested paths.

Test signals: `locks_test.go` covers remote caching, cache refresh, pagination, and verifiable cache behavior. API/schema tests in the package validate wire compatibility.
