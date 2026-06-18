<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_windows.go -->
# sources/sync-backup/restic/internal/terminal/background_windows.go

## Purpose
Provides the Windows implementation of background-process detection.

## Important APIs and Control Flow
`IsProcessBackground` always returns false because Unix process-group foreground/background semantics are not implemented here. There is no control flow beyond returning the safe default.

## State, Persistence, Dependencies, and Integration
No state is stored. It keeps shared terminal code portable on Windows.

## Risks and Test Signals
Risk is that Windows shells with similar concepts are ignored; callers should treat this as best-effort behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_windows.go -->
