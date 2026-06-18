# sources/object-store/minio-mc/cmd/config.go

Purpose: Central config path, load/save, alias lookup, environment alias, and alias expansion logic for mc.

Important APIs/types/functions: `setMcConfigDir`, `getMcConfigDir`, `defaultMCConfigDir`, `createMcConfigDir`, `getMcConfigPath`, `newMcConfig`, `loadMcConfigFactory`, `saveMcConfig`, `isMcConfigExists`, `cleanAlias`, `isValidAlias`, `getAliasConfig`, `mustGetHostConfig`, `parseEnvURLStr`, `readAliasesFromFile`, `expandAliasFromEnv`, `expandAlias`, and `mustExpandAlias`.

Control flow: Config path resolution honors custom directory first, then home plus platform-specific default. `saveMcConfig` creates the directory, persists v10, and refreshes the cached loader closure. Alias expansion checks `MC_HOST_<alias>`, then aliases loaded from `MC_CONFIG_ENV_FILE`, then persisted config.

State and persistence: Maintains `mcCustomConfigDir`, `loadMcConfig`, and `aliasToConfigMap`. Persists `config.json` through v10 helpers and reads environment config files line by line.

Dependencies/integration: Uses `homedir`, `env`, URL parsing, alias path joining, and error helpers. It is a core dependency for client creation, encryption key validation, and command URL expansion.

Risks: `parseEnvURLStr` uses regex credential extraction to preserve special characters, but URL edge cases remain sensitive. `aliasToConfigMap` is global and unsynchronized. `mustGetHostConfig` suppresses some errors by returning nil.

Test signals: `config_test.go` covers credential and session-token parsing, including special `@`, `#`, and empty user/password cases.
