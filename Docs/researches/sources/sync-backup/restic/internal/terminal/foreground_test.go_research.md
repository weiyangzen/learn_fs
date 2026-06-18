<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_test.go -->
# sources/sync-backup/restic/internal/terminal/foreground_test.go

## Purpose
Tests that foreground command execution scrubs restic environment variables.

## Important APIs and Control Flow
`TestForeground` sets `RESTIC_PASSWORD`, runs `env` through `StartForeground`, switches back via the returned function, then scans stdout for leaked password variables. Control flow waits for the command and checks scanner output.

## State, Persistence, Dependencies, and Integration
State is process environment and subprocess stdout. The test is non-Windows and depends on shell utilities.

## Risks and Test Signals
The signal is focused on secret hygiene; it does not fully validate process-group behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_test.go -->
