# sources/user-network-fs/rclone/fs/log.go

## Purpose
`fs/log.go` defines rclone's core logging API and log levels. It maps rclone's syslog-inspired levels onto `log/slog`, provides structured log values, gates messages by configured log level, implements panic/fatal helpers, and exposes convenience functions used across the codebase.

## Important APIs, types, and functions
Exports include `LogLevel`, level constants, `LogValueItem`, `LogValue`, `LogValueHide`, `LogLevelToSlog`, `LogPrint`, `LogPrintf`, `LogLevelPrint`, `LogLevelPrintf`, `Panic`, `Panicf`, `Fatal`, `Fatalf`, `Errorf`, `Logf`, `Infof`, `Debugf`, `LogDirName`, `PrettyPrint`, and `SetLogger`. Extra slog levels include notice, critical, alert, emergency, and off.

## Control flow
Callers invoke level-specific helpers. The wrappers compare `GetConfig(context.TODO()).LogLevel` to the requested level, format text and structured attributes, add object/objectType attributes when present, and send records to the package-level slog logger. Fatal helpers also detect rc job stack frames and panic instead of exiting when invoked inside an rc job.

## State and persistence behavior
The only state is the package-level `logger`, initially `slog.Default()` and later set by `fs/log/slog.go`. Logging output persistence is controlled by handlers in `fs/log`; this file itself does not open files or sinks.

## Dependencies and integration points
This API is imported throughout rclone. `fs/log/slog.go` calls `SetLogger`; `fs/log/log.go` installs reload hooks and output sinks. `Enum` support provides CLI/config parsing for `LogLevel`.

## Risks and edge cases
Fatal functions call `os.Exit(1)` outside rc jobs, so tests and libraries must avoid them unless expected. Structured `LogValueItem` arguments are extracted only from printf args, and hidden values render empty in text but remain structured. Caller code often passes arbitrary objects, so object formatting must avoid side effects.

## Test signals
`log_test.go` covers `LogValue` rendering/hiding and `LogLevel` string/set/JSON parsing. Handler formatting, levels, concurrency, and JSON behavior are covered in `fs/log/slog_test.go`.

Source-read signal: reviewed complete local file (348 lines). Types observed: `LogLevel`, `logLevelChoices`, `LogValueItem`. Functions/methods observed: `Choices`, `Type`, `LogValue`, `LogValueHide`, `String`, `LogLevelToSlog`, `logSlog`, `logSlogWithObject`, `LogPrint`, `LogPrintf`, `LogLevelPrint`, `LogLevelPrintf`, `Panic`, `Panicf`, `panicIfRcJob`, `Fatal`.
