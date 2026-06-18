<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go -->
# sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go

## Purpose
Provides AIX-specific foreground process-group assignment.

## Important APIs and Control Flow
`tcsetpgrp(fd,pid)` wraps the AIX terminal control operation required by `startForeground`. Control flow is a thin platform syscall adapter.

## State, Persistence, Dependencies, and Integration
No state beyond changing the terminal foreground process group. Integration is Unix foreground command execution.

## Risks and Test Signals
Risks are terminal state restoration failures and platform syscall differences; coverage is platform compile/runtime based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go -->
