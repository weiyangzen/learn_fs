# sources/sync-backup/kopia/repo/content/caching_options.go

Purpose: defines content/cache configuration values and small helpers used by repository read/write managers.

Important APIs/types/functions: `DurationSeconds` with `DurationOrDefault`; `CachingOptions` fields for cache directory, content and metadata size/limit bytes, list cache duration, sweep ages, and non-serialized `HMACSecret`; methods `EffectiveMetadataCacheSizeBytes`, `CloneOrDefault`, and `CacheSubdirOrEmpty`.

Control flow: duration helper returns default on zero. Effective metadata size falls back to content cache size for legacy configs. Clone handles nil by returning an empty options object. Cache subdir returns empty if cache or cache directory is unset.

State and persistence behavior: most fields serialize into local config; `HMACSecret` is intentionally excluded from JSON and supplied from repository format/security context.

Dependencies/integration: used by `repo/caching.go`, `committed_read_manager.go`, content caches, list cache, own-writes cache, and index blob cache.

Risks and edge cases: zero values are meaningful defaults, so callers must use helper methods instead of raw fields when default behavior matters. HMAC secret omission from JSON is security-sensitive.

Test signals: cache and committed content index tests indirectly exercise clone/default and sweep-age behavior.
