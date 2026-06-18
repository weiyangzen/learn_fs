## sources/sync-backup/kopia/internal/cache/content_cache_passthrough.go

Purpose: no-cache implementation of `ContentCache` used when caching is disabled.

Important APIs/types/functions: `passthroughContentCache`, `GetContent`, `PrefetchBlob`, `Sync`, `CacheStorage`, and `Close`.

Control flow, state, and persistence: `GetContent` ignores content ID and delegates directly to underlying storage `GetBlob`; prefetch/sync/close are no-ops; cache storage is nil. No cache state is persisted.

Dependencies and integration points: returned by `NewContentCache` when no base cache directory or explicit storage is configured.

Risks and test signals: includes a `Sync` method not present in `ContentCache`, likely for compatibility with broader cache interfaces. Tests cover passthrough reads for data and metadata configurations.
