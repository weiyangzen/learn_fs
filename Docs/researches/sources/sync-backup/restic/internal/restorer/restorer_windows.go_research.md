<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows.go -->
# sources/sync-backup/restic/internal/restorer/restorer_windows.go

## Purpose
Contains Windows-specific filename comparison behavior for restore delete logic.

## Important APIs and Control Flow
The helper normalizes comparable filenames for Windows so delete mode treats names case-insensitively. Control flow is used by `removeUnexpectedFiles` when building expected/actual filename sets.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with restore delete mode and Windows filesystem semantics.

## Risks and Test Signals
Risk is incomplete normalization for unusual Unicode/case-folding behavior; the Windows test suite includes a case-insensitive delete regression test.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows.go -->
