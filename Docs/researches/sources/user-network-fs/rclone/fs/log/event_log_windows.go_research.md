# sources/user-network-fs/rclone/fs/log/event_log_windows.go

## Purpose
`event_log_windows.go` implements Windows Event Log output for rclone logging. It installs/opens the `rclone` event source and adds an extra JSON logging destination that writes records into the Windows Application/Event Log infrastructure.

## Important APIs, types, and functions
Important items are `startWindowsEventLog`, `eventLog`, constants `errorID`, `infoID`, `sourceName`, and package variable `windowsEventLog`. `eventLog` maps rclone/slog levels onto Windows Error, Warning, or Info calls.

## Control flow
When enabled, `startWindowsEventLog` attempts source registration, opens the event log, stores the handle globally, registers a close hook via `atexit`, adds `eventLog` as a JSON extra output to `OutputHandler`, and logs activation. Each event checks `Opt.WindowsEventLogLevel` and writes to the appropriate event-log severity.

## State and persistence behavior
The Windows event-log handle is process-global and closed at exit. Log entries persist in the OS event log. Handler extra-output state is modified by appending a destination.

## Dependencies and integration points
The implementation depends on `golang.org/x/sys/windows/svc/eventlog`, `windows`, `atexit`, rclone `fs` levels, and `OutputHandler.AddOutput`. It is invoked only from `InitLogging`.

## Risks and edge cases
Source installation failure is ignored deliberately because Windows has fallbacks. Open failures are fatal through the caller. The global `windowsEventLog` must be non-nil when `eventLog` runs. Level filtering uses rclone levels converted to slog severity, so misconfiguration can drop expected events.

## Test signals
No direct test is present in this subset, likely due to platform requirements. Build tags and manual Windows logging tests are needed for end-to-end confidence.

Source-read signal: reviewed complete local file (79 lines). Functions/methods observed: `startWindowsEventLog`, `eventLog`.
