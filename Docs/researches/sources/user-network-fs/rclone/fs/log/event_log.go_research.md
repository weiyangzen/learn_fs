# sources/user-network-fs/rclone/fs/log/event_log.go

## Purpose
`event_log.go` is the non-Windows stub for Windows Event Log support. It makes the logging package compile on other platforms while reporting that the feature is unsupported.

## Important APIs, types, and functions
The single function is `startWindowsEventLog(*OutputHandler) error`, compiled when `!windows`. It returns a formatted error naming `runtime.GOOS`.

## Control flow
`InitLogging` calls `startWindowsEventLog` only when `Opt.WindowsEventLogLevel` is not off. On non-Windows platforms that configuration path returns an error, and `InitLogging` fatal-exits with context.

## State and persistence behavior
There is no state and no persistence. The stub does not create event sources or outputs.

## Dependencies and integration points
The file depends on `runtime` and `fmt`, and its signature matches the Windows implementation in `event_log_windows.go`. It integrates with the common logging initialization flow.

## Risks and edge cases
The stub protects against silently accepting unsupported `--windows-event-log-level` on non-Windows platforms. The fatal behavior occurs in the caller, not here.

## Test signals
No direct test in this subset targets the stub. Platform build coverage and option handling through `InitLogging` are the main signals.

Source-read signal: reviewed complete local file (15 lines). Functions/methods observed: `startWindowsEventLog`.
