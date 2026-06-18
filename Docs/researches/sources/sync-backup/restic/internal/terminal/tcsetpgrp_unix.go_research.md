<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go

## Purpose
Provides the default Unix foreground process-group assignment.

## Important APIs and Control Flow
`tcsetpgrp(fd,pid)` wraps the terminal ioctl/syscall used to move a process group into the foreground. It is called after starting the child and again in the cleanup closure to restore restic's process group.

## State, Persistence, Dependencies, and Integration
The persistent side effect is terminal foreground ownership until restored. It integrates with `foreground_unix.go`.

## Risks and Test Signals
Risks are leaving the terminal attached to the wrong group on error; foreground tests only cover the public path lightly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go -->
