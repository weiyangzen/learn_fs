# sources/object-store/minio/cmd/config.go

## Purpose
`config.go` implements current server config persistence, config history management, encrypted config read/write, and the `ConfigSys` initializer.

## Important APIs, Types, And Functions
Constants define config object prefixes and `config.json`. `listServerConfigHistory`, `delServerConfigHistory`, `readServerConfigHistory`, and `saveServerConfigHistory` manage `config/history/*.kv` entries. `saveServerConfig` marshals current config and optionally encrypts with `GlobalKMS`. `readServerConfig` reads/decrypts current config, returns defaults when missing, unmarshals with jsoniter, and merges missing entries. `ConfigSys.Init`, `NewConfigSys`, and `initConfig` drive boot-time config loading.

## Control Flow
History listing pages object listings, optionally reads/decrypts each entry, skips unreadable history data, and sorts by creation time. Current config reads from `.minio.sys/config/config.json` unless caller supplied bytes. Missing current config returns a default config after `lookupConfigs`; malformed/decryption errors propagate. `initConfig` calls migration-aware `readConfigWithoutMigrate`, applies env/runtime lookup, and swaps `globalServerConfig` under lock.

## State And Persistence Behavior
Current and history configs are objects under `.minio.sys`. If KMS is configured, values are encrypted with context binding to bucket/object path. Global in-memory config is updated after lookup.

## Dependencies And Integration Points
It integrates with object-layer list/read/write/delete, config common helpers, `GlobalKMS`, KMS encryption contexts, madmin config history APIs, json/jsoniter, migration, and runtime config lookup.

## Risks And Test Signals
History listing ignores unreadable/decrypt-failing entries, which favors resilience over strict audit completeness. Missing config silently produces defaults. Encryption context path changes would break decryption. Tests in this subset cover only basic current config initialization and madmin encryption primitives indirectly.
