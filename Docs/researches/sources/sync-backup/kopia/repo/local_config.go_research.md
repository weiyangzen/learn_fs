# sources/sync-backup/kopia/repo/local_config.go

Purpose: defines and persists local client configuration for connecting to either a remote API server or direct blob storage.

Important APIs/types/functions: `ClientOptions`, `ApplyDefaults`, `Override`, `UsernameAtHost`, `LocalConfig`, `writeToFile`, `LoadConfigFromFile`, and `ErrCannotWriteToRepoConnectionWithPermissiveCacheLoading`.

Control flow: defaults fill hostname, username, description, and format-blob cache duration. `writeToFile` clones caching options, stores cache directory relative to the config file when possible, creates the private config directory, and writes indented JSON atomically. Loading decodes JSON, resolves relative cache paths, honors absolute `KOPIA_CACHE_DIRECTORY`, and rejects permissive cache loading unless `KOPIA_UPGRADE_LOCK_ENABLED` is set.

State/persistence behavior: local config files persist storage/API connection data, caching options, read-only and action flags, throttling, and client identity. Directory mode is `0700`; file writing uses `atomicfile`.

Dependencies/integration: integrates `blob.ConnectionInfo`, `content.CachingOptions`, throttling limits, OS path helpers, and environment-variable overrides.

Risks/test signals: environment overrides can change cache location at load time; permissive cache loading is intentionally gated because it can be unsafe for write connections. Tests cover cache path round trip, nil caching, and missing-file errors.
