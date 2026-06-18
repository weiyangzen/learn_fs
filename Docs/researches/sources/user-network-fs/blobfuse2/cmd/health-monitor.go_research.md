<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor.go

Purpose: hidden `health-monitor` command that launches the external Blobfuse monitor binary for a running Blobfuse2 mount using the mount's config and process ID.

Important APIs/types/functions: `monitorOptions`, globals `pid` and `cacheMonitorOptions`, `resetMonitorOptions`, hidden `healthMonCmd`, `validateHMonOptions`, `buildCliParamForMonitor`, `parseConfig`, `config.UnmarshalKey`, `file_cache.FileCacheOptions`, and external command `hmcommon.BfuseMon`.

Control flow: reset monitor state, validate that `--pid` and `--config-file` are non-empty, parse the config, unmarshal `file_cache` and `health_monitor`, build bfusemon CLI parameters, execute `bfusemon`, log stdout if any, and disable monitoring on failure. `buildCliParamForMonitor` always passes the target pid, cache path, and max cache size, conditionally adds poll/output flags, and translates disable-list entries into `--no-*` flags.

State/persistence behavior: reads mount config and spawns a separate monitor process. It mutates `common.EnableMonitoring` to false on start failure and relies on the monitor binary for any output-path persistence. It uses package-global mount options shared with the mount command.

Dependencies/integration: started by `mount.go` through `startMonitor`, relies on `bfusemon` being installed or in PATH, and shares constants with `tools/health-monitor/common`. It depends on valid file-cache config even when file-cache monitoring is disabled.

Risks/test signals: missing `bfusemon`, invalid config, or empty pid/config flags produce command errors. Disable-list values that are not recognized are only debug logged. Tests cover option validation, CLI param construction, invalid config paths, external-start failure, and stop command failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor.go -->
