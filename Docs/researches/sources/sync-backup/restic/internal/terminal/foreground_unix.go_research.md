<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_unix.go -->
# sources/sync-backup/restic/internal/terminal/foreground_unix.go

## Purpose
Implements Unix foreground process handling for subprocesses.

## Important APIs and Control Flow
`startForeground` sets the child in its own process group, opens `/dev/tty`, checks restic owns the foreground, ignores `SIGTTIN`/`SIGTTOU`, starts the command, moves the child process group to the foreground, and returns a cleanup function that restores the previous process group and signal handling. If `/dev/tty` is unavailable or restic is not foreground, it falls back to plain `cmd.Start`.

## State, Persistence, Dependencies, and Integration
State includes terminal foreground process group and process signal dispositions during the child run. Dependencies are `golang.org/x/sys/unix`, `tcgetpgrp`, `tcsetpgrp`, and `os/signal`.

## Risks and Test Signals
Risks are leaving terminal process groups or signals in a bad state on errors. The foreground environment test covers public behavior; direct process-group behavior is mainly exercised manually/implicitly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_unix.go -->
