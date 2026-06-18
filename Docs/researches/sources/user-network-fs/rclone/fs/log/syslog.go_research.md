# sources/user-network-fs/rclone/fs/log/syslog.go

## Purpose
`syslog.go` is the unsupported-platform stub for syslog integration.

## Important APIs, types, and functions
The single function is `startSysLog(handler *OutputHandler) bool`, compiled for Windows, NaCl, and Plan 9. It calls `fs.Fatalf` with a platform-specific unsupported message and returns false only for compile-time completeness.

## Control flow
When `--syslog` is configured on unsupported platforms, `InitLogging` calls this stub and the process exits via fatal logging.

## State and persistence behavior
No syslog state is created and no persistence occurs beyond the fatal log/exit.

## Dependencies and integration points
It depends on `runtime` and rclone `fs.Fatalf`. The signature matches `syslog_unix.go`.

## Risks and edge cases
The explicit fatal avoids silently logging to the wrong sink when users request syslog. Library users should avoid enabling syslog on these platforms unless they expect process exit.

## Test signals
No direct tests are present. Build tags and platform CLI tests are the relevant coverage.

Source-read signal: reviewed complete local file (17 lines). Functions/methods observed: `startSysLog`.
