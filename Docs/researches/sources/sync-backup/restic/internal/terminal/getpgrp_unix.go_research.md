<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/getpgrp_unix.go

## Purpose
Provides the default Unix process group lookup.

## Important APIs and Control Flow
`getpgrp` returns the current process group using the platform syscall. Control flow is a thin wrapper used by background and foreground terminal code.

## State, Persistence, Dependencies, and Integration
No persistent state. It is selected for Unix platforms except special cases such as Solaris.

## Risks and Test Signals
Risk is limited to platform compatibility; behavior is indirectly tested by terminal Unix tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_unix.go -->
