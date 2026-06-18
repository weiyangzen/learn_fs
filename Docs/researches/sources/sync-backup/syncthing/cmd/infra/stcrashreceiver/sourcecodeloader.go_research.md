# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sourcecodeloader.go

Purpose: raven-go source-code loader that fetches Syncthing source context from GitHub for stack frames in crash reports.

Important APIs/types/functions: constants `urlPrefix`, `httpTimeout`, and `maxCacheEntries`; `cacheKey`; `githubSourceCodeLoader` with mutex, current version, 2Q LRU cache, and HTTP client; methods `LockWithVersion`, `Unlock`, and `Load`; helper `getLineFromLines`.

Control flow: Sentry parsing locks the loader to a version. `Load` normalizes filename, checks cache, identifies `/lib/` or `/cmd/` path segment, fetches raw GitHub content at version plus repo-relative suffix, splits into lines, caches success or nil failure, updates metrics, then returns requested context lines and the target-line index.

State and persistence behavior: in-memory LRU cache keyed by version and file; current version protected by mutex; metrics track loads/cache size.

Dependencies/integration: integrated with raven-go via `raven.SetSourceCodeLoader`, GitHub raw content, panic stack frames, and Prometheus metrics.

Risks/test signals: only `/lib/` and `/cmd/` paths get source context, so other packages are ignored. Network failures are cached as nil for that key, avoiding repeated requests but hiding transient recovery until eviction. Signals are `loaded`, `cached`, and `failed` metrics plus source context appearing in Sentry events.
