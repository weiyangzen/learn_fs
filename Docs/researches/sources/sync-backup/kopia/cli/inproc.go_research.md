<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/inproc.go -->
# sources/sync-backup/kopia/cli/inproc.go

## Purpose
Provides in-process CLI execution for tests and embedded callers, returning stdout/stderr readers plus wait and interrupt functions.

## Important APIs, Types, And Functions
Defines `App.RunSubcommand`. It creates pipes, redirects app IO/logging, sets simulated Ctrl-C state, attaches commands, parses args in a goroutine, captures exit errors, closes resources, and returns an interrupt closure.

## Control Flow
The caller receives pipe readers immediately. The goroutine parses and runs the selected command, then sends parse or exit errors on a result channel. Interrupt sends `true` on `simulatedCtrlC`.

## State And Persistence Behavior
State is per-App mutable test state: stdin/stdout/stderr writers, root context logger, simulatedCtrlC channel, `isInProcessTest`, and `exitWithError` override.

## Dependencies And Integration Points
Integrates Kingpin parsing, internal releasable tracking, repository logging to stderr, and termination callback logic in `config.go`.

## Risks And Edge Cases
This mutates the App instance, so concurrent in-process runs on the same App would interfere. If command code blocks writing to pipes and caller does not drain, deadlock is possible.

## Test Signals
Used broadly by CLI tests. Specific tests should verify stdout/stderr capture, parse error propagation, exit error propagation, and simulated interrupt behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/inproc.go -->
