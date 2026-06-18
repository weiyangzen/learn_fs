<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows.go -->
# sources/sync-backup/restic/internal/terminal/terminal_windows.go

## Purpose
Implements Windows console and mintty-aware terminal status operations.

## Important APIs and Control Flow
`ClearCurrentLine`, `MoveCursorUp`, and `MoveCursorDown` choose native Windows console APIs or POSIX escape functions based on `isWindowsTerminal`. `CanUpdateStatus` returns true for native terminals and mintty/cygwin pty master pipes detected through handle names. Native clear/move functions call `GetConsoleScreenBufferInfo`, `FillConsoleOutput*`, and `SetConsoleCursorPosition`.

## State, Persistence, Dependencies, and Integration
State is terminal cursor and screen buffer contents. Dependencies are `golang.org/x/sys/windows`, `golang.org/x/term`, and kernel32 procedures.

## Risks and Test Signals
Risks are unsafe syscall argument handling, false positives for pipe terminal detection, and output corruption. Tests cover mintty pty-vs-pipe detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows.go -->
