<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/stdio.go -->
# sources/sync-backup/restic/internal/terminal/stdio.go

## Purpose
Defines standard input/output handles used by terminal implementations.

## Important APIs and Control Flow
The file exposes process stdio variables/wrappers so terminal code can be tested or swapped consistently. Control flow is minimal; these handles are consumed by terminal construction and prompt/status output.

## State, Persistence, Dependencies, and Integration
State is the process stdio descriptors. Integration is with password reading, foreground/background checks, and UI terminal output.

## Risks and Test Signals
Risks are global handle mutation in tests and redirected stdio behavior; platform terminal tests cover update capability separately.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/stdio.go -->
