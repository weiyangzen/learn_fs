# sources/user-network-fs/rclone/fs/log/systemd_unix.go

## Purpose
`systemd_unix.go` implements systemd journal output and journal-stream autodetection for Unix builds.

## Important APIs, types, and functions
Exports within the package are `startSystemdLog`, `slogLevelToSystemdPriority`, and `isJournalStream`. `slogLevelToSystemdPrefix` maps rclone/slog levels to `journal.Priority` values.

## Control flow
When enabled, `startSystemdLog` strips standard timestamp/file/PID format flags, forces no text level prefix, and replaces the handler output with a function that calls `journal.Print` using the mapped priority and formatted level/text. `isJournalStream` delegates to `journal.StderrIsJournalStream` for autodetection.

## State and persistence behavior
The handler output is redirected process-wide to journald. Log records persist according to systemd journal configuration. No local files are created by this file.

## Dependencies and integration points
It depends on `github.com/coreos/go-systemd/v22/journal`, `log/slog`, rclone levels, and `OutputHandler`. `InitLogging` calls it when `--log-systemd` is set or when stderr is detected as a journal stream and output is not redirected elsewhere.

## Risks and edge cases
Unknown slog levels default to info priority. `journal.Print` errors are ignored. Handler format mutation affects all subsequent logging. Autodetection only checks stderr and is bypassed when logs are redirected to file/syslog.

## Test signals
No direct test is present in this subset. Manual systemd-run/journalctl checks are needed for full behavior.

Source-read signal: reviewed complete local file (48 lines). Functions/methods observed: `startSystemdLog`, `slogLevelToSystemdPriority`, `isJournalStream`.
