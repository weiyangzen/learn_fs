<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_windows.go -->
# sources/sync-backup/restic/internal/terminal/foreground_windows.go

## Purpose
Implements Windows foreground command handling.

## Important APIs and Control Flow
`startForeground` starts the command using Windows process attributes and returns a no-op background restoration function. Control flow is intentionally simpler than Unix because Windows does not use POSIX terminal process groups.

## State, Persistence, Dependencies, and Integration
State is the spawned process configured through `exec.Cmd`/Windows syscall attributes. Integration is through `StartForeground` after environment scrubbing.

## Risks and Test Signals
Risks are Windows console control behavior and command start errors; there is no dedicated Windows foreground test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_windows.go -->
