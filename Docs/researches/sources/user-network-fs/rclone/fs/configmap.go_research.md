<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/configmap.go -->
# sources/user-network-fs/rclone/fs/configmap.go

## Purpose
Builds layered config lookup maps for backend/global options, merging connection strings, explicit option values, environment variables, config file values, and defaults.

## Important APIs, Types, And Control Flow
Getter types include `configEnvVars` for `RCLONE_CONFIG_REMOTE_KEY`, `optionEnvVars` for backend/global `RCLONE_*` options with no-prefix fallback, `regInfoValues` for defaults or non-default flags, and `getConfigFile`. `setConfigFile` writes values through `ConfigFileSet`. `ConfigMap` orders getters from highest priority connection-string/flag/remote-env/backend-env/config-file/default and attaches the config-file setter.

## State And Persistence
Reads process environment and config-file storage. Setters persist to the active config file/storage layer via config helpers.

## Dependencies And Integration Points
Depends on `fs/config/configmap`, option metadata, environment naming helpers, and config file get/set functions. Backend initialization uses this to resolve option values.

## Risks And Test Signals
Priority order is critical: changing it can alter compatibility. Empty config-file values are treated as absent. No direct tests here, but many backend/config tests indirectly depend on this resolution path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/configmap.go -->
