# sources/user-network-fs/rclone/fs/log/slog_test.go

## Purpose
`slog_test.go` is the unit and concurrency test suite for rclone's custom slog `OutputHandler`.

## Important APIs, types, and functions
Tests cover `slogLevelToString`, `mapLogLevelNames`, `getCaller`, `isLogFrame`, `NewOutputHandler`, `formatStdLogHeader`, `Enabled`, `clearFormatFlags`, `setFormatFlags`, `SetOutput`, `ResetOutput`, `AddOutput`, `Handle`, `WithAttrs`, `WithGroup`, `textLog`, and `jsonLog`.

## Control flow
The suite uses a fixed timestamp and buffers to assert exact or prefix/suffix output. It constructs records with levels and attrs, runs handler methods, and checks text or JSON output. `TestOutputHandlerConcurrency` launches goroutines that simultaneously call `Handle`, mutate formats, mutate level, override outputs, and clone handlers, then fails on timeout to catch deadlocks.

## State and persistence behavior
All test state is in-memory buffers, fixed time values, and goroutine synchronization. No log files or OS logging systems are used.

## Dependencies and integration points
The tests use Go `log/slog`, runtime frame data, regex, time zones, and rclone `fs` slog levels. They protect the handler used by all rclone logging entry points and the platform output adapters.

## Risks and edge cases
Exact formatting expectations are sensitive to level field width, PID inclusion, UTC conversion, JSON attribute names, and caller source paths. Concurrency coverage is timeout-based, so it catches deadlocks more than subtle data races unless run with `-race`.

## Test signals
Coverage is broad and directly targets the most failure-prone handler code: mixed JSON/text destinations, output override stacks, frame skipping under trimpath, dynamic format changes, and concurrent logging/reconfiguration.

Source-read signal: reviewed complete local file (402 lines). Functions/methods observed: `TestSlogLevelToString`, `TestMapLogLevelNames`, `TestGetCaller`, `TestIsLogFrame`, `TestFormatStdLogHeader`, `TestEnabled`, `TestClearSetFormatFlags`, `TestSetResetOutput`, `TestAddOutput`, `TestAddOutputJSON`, `TestAddOutputUseJSONLog`, `TestJSONLogWithPid`, `TestWithAttrsAndGroup`, `TestTextLogAndJsonLog`, `TestOutputHandlerConcurrency`, `TestHandleFormatFlags`.
