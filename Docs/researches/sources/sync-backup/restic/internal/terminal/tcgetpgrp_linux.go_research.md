<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go -->
# sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go

## Purpose
Provides Linux-specific `tcgetpgrp` implementation.

## Important APIs and Control Flow
`tcgetpgrp(fd)` calls the appropriate ioctl/syscall to read the foreground process group for a terminal descriptor. It returns the process group ID or an error to callers in background/foreground logic.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with `IsProcessBackground` and Unix `startForeground`.

## Risks and Test Signals
Risks are ioctl portability and descriptor validity. Unix terminal tests exercise the call when `/dev/tty` is available.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go -->
