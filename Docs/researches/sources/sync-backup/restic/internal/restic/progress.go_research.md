<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress.go -->
# sources/sync-backup/restic/internal/restic/progress.go

## Purpose
Defines the minimal progress counter interfaces used by core repository helpers without depending on UI packages.

## Important APIs and Control Flow
`Counter` exposes `Add`, `SetMax`, `Get`, and `Done`; `noopCounter` and `NoopCounter` implement a safe no-op counter. `noopTerminalCounterFactory` implements `TerminalCounterFactory.NewCounterTerminalOnly` by returning the no-op counter. There is no control flow beyond method dispatch; callers can always install a counter and skip nil checks.

## State, Persistence, Dependencies, and Integration
No state is persisted. The file integrates low-level restic packages with terminal/UI progress implementations through interfaces declared in `repository.go`.

## Risks and Test Signals
The main risk is interface drift between core and UI progress implementations. Tests assert that all no-op methods are callable and return `(0,0)` without panics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress.go -->
