# sources/sync-backup/syncthing/lib/locations/locations_test.go

## Purpose
Tests Unix location defaulting and timestamped path formatting.

## Important APIs, Types, and Functions
`TestUnixConfigDir`, `TestUnixDataDir`, and `TestGetTimestamped` call internal helpers `unixConfigDir`, `unixDataDir`, and `getTimestampedAt`.

## Control Flow
The Unix tests define table rows with user home, XDG variables, simulated existing files, and expected directories. Each row injects a `fileExists` closure backed by `slices.Contains`. The timestamp test fixes a UTC time and checks the basename of `PanicLog`.

## State and Persistence Behavior
No filesystem writes occur. Tests simulate existence entirely in memory. `TestGetTimestamped` reads the package global `locations` map initialized by `init`.

## Dependencies and Integration Points
Build-tagged `!windows`, so these tests validate Unix-like behavior only. They protect upgrade paths from legacy `.config/syncthing` and old LevelDB database locations to current state directory rules.

## Risks
The tests do not cover relative XDG state rejection directly for every branch, Windows/Darwin paths, `Set`, `SetBaseDir`, or concurrent global mutation. They also assume initialized templates include `%{timestamp}` for `PanicLog`.

## Test Signals
Strong signal on migration-sensitive precedence: existing config wins over new state defaults, existing database can keep data colocated with config or legacy XDG data, and timestamp formatting uses `YYYYMMDD-HHMMSS`.
