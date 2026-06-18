<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_windows.go -->
# sources/sync-backup/restic/internal/restic/uid_windows.go

## Purpose
Provides the Windows implementation of uid/gid conversion for code paths that need a cross-platform symbol.

## Important APIs and Control Flow
`UidGidInt` ignores the supplied user and returns zero uid, zero gid, and nil error. Control flow is intentionally trivial because Windows metadata restoration uses different attributes and ACL concepts.

## State, Persistence, Dependencies, and Integration
There is no state or persistence. The file is selected by build tags through filename suffix and keeps shared code compiling on Windows.

## Risks and Test Signals
Risk is accidental use of zero uid/gid as meaningful Windows ownership data; platform-specific restore code should rely on Windows metadata instead.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_windows.go -->
