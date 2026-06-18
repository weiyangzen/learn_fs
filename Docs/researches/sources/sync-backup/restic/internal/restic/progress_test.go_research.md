<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress_test.go -->
# sources/sync-backup/restic/internal/restic/progress_test.go

## Purpose
Smoke-tests the no-op progress implementations used by core restic packages.

## Important APIs and Control Flow
`TestNoopCounter` calls `Add`, `SetMax`, `Get`, and `Done` through `NoopCounter` and exercises `NoopTerminalCounterFactory.NewCounterTerminalOnly`. The test verifies no panic and zero-valued progress state rather than formatting or timing behavior.

## State, Persistence, Dependencies, and Integration
There is no persistent state. Integration is with the `Counter` and `TerminalCounterFactory` interfaces used by repository and UI code.

## Risks and Test Signals
The signal is intentionally narrow: it catches interface drift but not real UI counter behavior, which is covered in `internal/ui/progress` tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress_test.go -->
