<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go

## Purpose
Provides the default Unix `tcgetpgrp` implementation for non-Linux Unix platforms.

## Important APIs and Control Flow
`tcgetpgrp` wraps the platform terminal ioctl for foreground process-group lookup. Control flow is a syscall wrapper returning process group ID and errors.

## State, Persistence, Dependencies, and Integration
No persistent state. It supports terminal foreground/background code on BSD-like systems.

## Risks and Test Signals
Risk is platform ioctl incompatibility; coverage is build/platform based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go -->
