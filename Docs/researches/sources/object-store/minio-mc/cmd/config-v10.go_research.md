# sources/object-store/minio-mc/cmd/config-v10.go

Purpose: Defines and persists current config schema version 10 for mc aliases.

Important APIs/types/functions: `aliasConfigV10`, `configV10`, `newConfigV10`, `setAlias`, `loadDefaults`, `loadConfigV10`, and `saveConfigV10`. Globals `cacheCfgV10` and `cfgMutex` cache and synchronize config file access.

Control flow: `loadConfigV10` returns cached config when available, rejects missing config files, creates a quick config loader, loads `config.json`, caches it, and returns it. `saveConfigV10` locks for writing, updates the cache, and saves through `quick`.

State and persistence: Owns the in-memory v10 cache and writes/reads the JSON config path from `mustGetMcConfigPath`.

Dependencies/integration: Depends on `probe`, `quick`, config path helpers, and `globalMCConfigVersion`. Used by `loadMcConfigFactory` and `saveMcConfig`.

Risks: The load path takes an `RLock` while assigning `cacheCfgV10`; that relies on process ordering and could be a race under concurrent first loads. Cache invalidation only happens through `saveMcConfig`.

Test signals: Covered indirectly by config tests; no direct persistence test here.
