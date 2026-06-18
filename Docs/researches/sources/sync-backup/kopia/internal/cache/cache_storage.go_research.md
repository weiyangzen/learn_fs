## sources/sync-backup/kopia/internal/cache/cache_storage.go

Purpose: creates a filesystem-backed storage for cache contents and defines the reduced storage interface required by caches.

Important APIs/types/functions: `Storage`, `DirMode`, `NewStorageOrNil`, `filesystemImplWrapper`, and testable `mkdirAll`.

Control flow, state, and persistence: returns nil when cache size or base directory disables caching; rejects relative cache paths; ensures the cache subdirectory exists; opens a sharded filesystem blob storage using `context.WithoutCancel`; wraps it to expose only cache storage methods. Persistent state is the on-disk cache directory.

Dependencies and integration points: integrates `repo/blob/filesystem` and `sharded` storage with content cache. Touch support is required by persistent cache expiration.

Risks and test signals: type assertion assumes filesystem storage implements `cache.Storage`. Directory creation and initialization errors are wrapped. Tests cover disabled caching, relative paths, and mkdir failure.
