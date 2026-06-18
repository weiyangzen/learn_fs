<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix.go -->
# sources/sync-backup/restic/internal/restorer/restorer_unix.go

## Purpose
Contains Unix-specific filename comparison behavior for restore delete logic.

## Important APIs and Control Flow
The platform helper keeps filenames comparable using the native case-sensitive representation. Control flow is a small conversion function used when building the keep-set in `removeUnexpectedFiles`.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with `Restorer.removeUnexpectedFiles` and is selected on Unix platforms.

## Risks and Test Signals
Risk is platform mismatch if mounted filesystems have non-standard case behavior. Windows has a separate implementation for case-insensitive comparison.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix.go -->
