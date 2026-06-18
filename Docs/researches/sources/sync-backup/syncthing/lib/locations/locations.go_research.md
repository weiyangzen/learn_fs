# sources/sync-backup/syncthing/lib/locations/locations.go

## Purpose
Centralizes Syncthing runtime path selection for config, certificates, database, logs, GUI assets, default folder, and lock files. It also computes platform defaults and expands timestamped log paths.

## Important APIs, Types, and Functions
`LocationEnum` and `BaseDirEnum` enumerate keys. Public functions are `Set`, `SetBaseDir`, `Get`, `GetBaseDir`, `ListExpandedPaths`, `PrettyPaths`, and `GetTimestamped`. Internal helpers include `expandLocations`, platform default functions, `unixConfigDir`, `unixDataDir`, `userHomeDir`, `getTimestampedAt`, and `fileExists`.

## Control Flow
`init` resolves user home, config base, and data base, populates `baseDirs`, then expands templates into `locations`. `Set` validates location keys and stores an absolute cleaned override, except `"-"`. `SetBaseDir` validates base keys, absolutizes the path, updates `baseDirs`, and recomputes all template-derived locations. Unix default selection prefers existing legacy config or database paths, then absolute `XDG_STATE_HOME`, then `~/.local/state/syncthing`.

## State and Persistence Behavior
The package keeps process-global mutable maps `baseDirs` and `locations`. It does not write files, but it probes existence with `os.Lstat` and reads environment variables. Timestamp expansion is computed on demand without mutating stored templates.

## Dependencies and Integration Points
Uses `build` platform flags, `fs.ExpandTilde`, `filepath`, `os`, and `time`. Model health checks use `locations.Get(locations.Database)` to verify database disk free space; command-line and startup code can override paths through this package.

## Risks
Global mutable maps are not guarded by locks, so path overrides are expected during startup, not concurrent runtime mutation. Environment handling intentionally preserves historical behavior for relative XDG config/data variables, which can surprise strict XDG consumers. `init` panics on expansion failure.

## Test Signals
`locations_test.go` validates Unix config/data fallback order and timestamp substitution. Platform-specific Windows/Darwin defaults are not exercised in this listed test file.
