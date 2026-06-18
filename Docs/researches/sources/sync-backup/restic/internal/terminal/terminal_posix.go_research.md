<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_posix.go -->
# sources/sync-backup/restic/internal/terminal/terminal_posix.go

## Purpose
Implements POSIX escape-sequence helpers for terminal status updates.

## Important APIs and Control Flow
`PosixClearCurrentLine`, cursor-home/up/down constants, and movement helpers write ANSI control sequences to an `io.Writer`. Control flow writes clear/move sequences and can be selected on POSIX terminals or mintty-like Windows pipes.

## State, Persistence, Dependencies, and Integration
State is terminal cursor/display state, not application persistence. It integrates with UI status rendering.

## Risks and Test Signals
Risks are escape sequences going to non-terminal outputs and display corruption if width/cursor assumptions are wrong.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_posix.go -->
