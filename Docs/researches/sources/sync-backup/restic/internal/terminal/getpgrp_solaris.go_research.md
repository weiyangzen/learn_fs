<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go -->
# sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go

## Purpose
Provides Solaris-specific process group lookup.

## Important APIs and Control Flow
`getpgrp` calls the Solaris-compatible syscall variant needed by terminal foreground/background code. Control flow is a thin syscall wrapper.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with Unix terminal process-group comparisons.

## Risks and Test Signals
Risk is platform syscall drift; coverage is compile/platform based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go -->
