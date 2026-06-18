<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix.go -->
# sources/sync-backup/restic/internal/terminal/background_unix.go

## Purpose
Detects whether the current process is running in the background on Unix terminals.

## Important APIs and Control Flow
`IsProcessBackground` wraps `isProcessBackground`; the internal helper compares the terminal foreground process group from `tcgetpgrp(fd)` with `getpgrp()`. Errors are logged and treated as foreground/default behavior to avoid blocking normal operation.

## State, Persistence, Dependencies, and Integration
No persistent state. It depends on terminal process-group syscalls and `debug.Log`, and integrates with terminal prompt/status behavior.

## Risks and Test Signals
Risks are syscall failures in non-interactive sessions and incorrect defaults for background jobs. The Unix test opens `/dev/tty` when available and verifies the helper returns without error.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix.go -->
