# sources/sync-backup/kopia/repo/caching.go

Purpose: reads and updates repository-local caching options and resolves default cache directories.

Important APIs/types/functions: `GetCachingOptions`, `SetCachingOptions`, and `setupCachingOptionsWithDefaults` operate on `LocalConfig` and `content.CachingOptions`.

Control flow: reads load config and return `CloneOrDefault`. Setting options loads config, normalizes options, computes cache directory defaults when content cache is enabled, copies cache size/duration fields into local config, and writes the config file. If content cache size is zero, caching is reset to an empty options object.

State and persistence behavior: modifies the repository local config file. Default cache directory is `$UserCacheDir/kopia/<sha256(uniqueID || configPath)[:16]>`, which makes it stable per repository/config while avoiding collisions. Custom directories are stored as absolute paths.

Dependencies/integration: used by connect/open/config commands and content manager cache setup. Depends on OS cache directory discovery, SHA-256, and `content.CachingOptions`.

Risks and edge cases: when `uniqueID` is nil, hashing uses only config path, which is appropriate for post-connect updates but less repository-specific. Failure to resolve user cache or absolute custom path blocks setting cache options.

Test signals: covered indirectly by repository connect/open and cache manager tests; direct tests should verify default path stability and reset behavior.
