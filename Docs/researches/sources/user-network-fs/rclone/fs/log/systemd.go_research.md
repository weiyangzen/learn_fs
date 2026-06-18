# sources/user-network-fs/rclone/fs/log/systemd.go

## Purpose
`systemd.go` is the unsupported-platform stub for systemd journal logging.

## Important APIs, types, and functions
It implements `startSystemdLog(handler *OutputHandler) bool` and `isJournalStream() bool` for `!unix` builds. `startSystemdLog` fatal-exits when configured; `isJournalStream` returns false.

## Control flow
`InitLogging` may call `isJournalStream` for autodetection and `startSystemdLog` when systemd logging is requested. On non-Unix builds autodetection is disabled and explicit enablement is fatal.

## State and persistence behavior
There is no state and no journal output on these platforms.

## Dependencies and integration points
The stub depends on `runtime` and rclone `fs.Fatalf`. It matches the Unix implementation's API so `log.go` remains portable.

## Risks and edge cases
Explicit `--log-systemd` is not silently ignored; it terminates on unsupported platforms. This is appropriate for CLI clarity but can surprise embedded callers.

## Test signals
No direct test is present. Build coverage verifies the stub compiles.

Source-read signal: reviewed complete local file (21 lines). Functions/methods observed: `startSystemdLog`, `isJournalStream`.
