# sources/user-network-fs/rclone/fs/log/syslog_unix.go

## Purpose
`syslog_unix.go` implements syslog output on supported Unix-like platforms.

## Important APIs, types, and functions
Important items are `syslogFacilityMap` and `startSysLog(handler *OutputHandler) bool`. The map translates facility strings such as `DAEMON`, `LOCAL0`, and `AUTHPRIV` to `syslog.Priority` values.

## Control flow
`startSysLog` validates `Opt.SyslogFacility`, opens a syslog writer with program basename, strips date/time/file/PID format flags, forces no textual level prefix, and installs a handler output function. That function maps slog/rclone levels to syslog methods such as `Emerg`, `Alert`, `Crit`, `Err`, `Warning`, `Notice`, `Info`, and `Debug`.

## State and persistence behavior
The syslog writer is captured in a closure stored as the handler output. Log records persist through the system syslog service. Handler format/output state is mutated globally.

## Dependencies and integration points
It uses Go `log/syslog`, `os.Args`, `path.Base`, rclone levels, and `OutputHandler`. `InitLogging` calls it when `Opt.UseSyslog` is set and rejects simultaneous log-file output.

## Risks and edge cases
Unknown facilities and syslog open failures are fatal. The writer is not explicitly closed here. Format mutation changes global handler behavior. Syslog availability varies by Unix platform and runtime environment.

## Test signals
No direct test is present in this subset. Manual or integration testing should cover facility validation, level mapping, and environments without a syslog daemon.

Source-read signal: reviewed complete local file (75 lines). Functions/methods observed: `startSysLog`.
