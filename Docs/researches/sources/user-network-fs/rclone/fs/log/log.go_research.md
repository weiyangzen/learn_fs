# sources/user-network-fs/rclone/fs/log/log.go

## Purpose
`fs/log/log.go` owns high-level logging configuration and initialization. It registers global logging options, defines log-format flags, trace/stack helpers, reload validation, file/syslog/systemd/event-log setup, JSON-log implication, and stderr redirection decisions.

## Important APIs, types, and functions
Exports are `OptionsInfo`, `Options`, `Opt`, `Trace`, `Stack`, `InitLogging`, and `Redirected`. Internal pieces include `logFormat` bit flags, `logFormatChoices`, `fnName`, `logReload`, and `fs.LogReload` assignment. Options cover log file, rotation, format, syslog, systemd, and Windows Event Log level.

## Control flow
`init` registers options and reload hook. `InitLogging` sets the process default slog logger to rclone's handler, maps standard log output to notice, opens file output or lumberjack rotation if configured, applies JSON formatting, sets initial level and format, starts syslog if requested, autodetects journald when stderr is not redirected, enables systemd output, and starts Windows event logging when configured.

## State and persistence behavior
`Opt` is global config state. `InitLogging` mutates process-wide slog defaults and the global `Handler`. File logging persists to a configured file or rotated lumberjack files. Syslog/systemd/Event Log output persists through OS logging systems. `Trace`/`Stack` only emit when debug logging is active.

## Dependencies and integration points
This file coordinates `fs` config, `OutputHandler` from `slog.go`, platform files for stderr/syslog/systemd/event logs, `lumberjack` rotation, and the CLI/global option system. It is called by CLI, librclone, and tests rather than package init to avoid import side effects.

## Risks and edge cases
`--syslog` and `--log-file` are mutually exclusive. File mode without rotation redirects stderr for panic capture; rotated mode does not redirect stderr in the same way. Journald autodetection changes formatting. `logReload` validates Windows event log level relative to main log level. Fatal setup errors exit the process.

## Test signals
Direct tests for this file are limited in the subset; `slog_test.go` covers the handler underneath and platform behavior needs integration/manual testing. The option registration is exercised by normal CLI startup.

Source-read signal: reviewed complete local file (304 lines). Types observed: `Options`, `logFormat`, `logFormatChoices`. Functions/methods observed: `init`, `Choices`, `fnName`, `Trace`, `Stack`, `logReload`, `init`, `InitLogging`, `Redirected`.
