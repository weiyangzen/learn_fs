# sources/sync-backup/restic/internal/backend/cache/cache.go

Purpose: Manages cache directory creation, layout, versioning, age detection, and backend wrapping.

Important APIs and types: `Cache` stores the repo cache path, base path, creation flag, and `forgotten` circuit-breaker map. `New`, `readVersion`, `writeCachedirTag`, `All`, `OlderThan`, `Old`, `IsOld`, `Wrap`, and `BaseDir` are the main functions. Constants define directory/file modes, cache version, cacheable subpaths, CACHEDIR.TAG signature, and max cache age.

Control flow and state: `New` resolves the base directory, creates it, writes `CACHEDIR.TAG`, opens or creates the repo-specific cache directory, validates/updates the version file, updates directory timestamps, creates data/snapshots/index subdirectories, and returns a `Cache`. Directory listing filters only valid 64-hex IDs and check-cache names.

Persistence and dependencies: Persists `CACHEDIR.TAG`, `version`, and cache subdirectories on disk. Uses `os`, `filepath`, regex validation, timestamps, and `pkg/errors`.

Integration points: Called by command setup and tests to create caches; `Wrap` integrates with `cacheBackend`; `Old`/`OlderThan` support cache cleanup commands.

Risks and test signals: Risks include version incompatibility, missing tag/version recreation, permissions, invalid directory cleanup, and timestamp-based old-cache detection. `cache_test.go` validates creation, tag recreation, and version recreation.
