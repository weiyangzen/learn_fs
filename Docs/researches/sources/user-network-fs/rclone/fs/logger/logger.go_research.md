# sources/user-network-fs/rclone/fs/logger/logger.go

## Purpose
`logger.go` provides the testscript entry point for rclone logger-related CLI tests. It builds a test executable function with all backends, commands, and plugins imported.

## Important APIs, types, and functions
The single public API is `Main()`, which delegates to `cmd.Main()`. Blank imports register `backend/all`, `cmd/all`, and `lib/plugin`.

## Control flow
`logger_test.go` registers `logger.Main` under the command name `rclone` for the `testscript` framework. When a script invokes `rclone`, control enters `cmd.Main` with the current testscript process environment.

## State and persistence behavior
This file itself stores no state. Runtime state is whatever `cmd.Main` and registered backends/commands create under testscript's temporary work directories.

## Dependencies and integration points
It integrates rclone's command package with `rogpeppe/go-internal/testscript`. The broad blank imports ensure script tests see the normal CLI command/backend registry.

## Risks and edge cases
Importing all backends/commands can increase test startup cost and pull in global init behavior. The package is test-support-oriented and should not be used as a production abstraction.

## Test signals
`logger_test.go` uses this entry point to execute scripts under `testdata/script`, giving end-to-end CLI coverage for sync/bisync logger behavior.

Source-read signal: reviewed complete local file (16 lines). Functions/methods observed: `Main`.
