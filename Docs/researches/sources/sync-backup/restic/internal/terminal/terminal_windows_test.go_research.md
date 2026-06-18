<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows_test.go -->
# sources/sync-backup/restic/internal/terminal/terminal_windows_test.go

## Purpose
Tests Windows mintty/cygwin pipe detection for status updates.

## Important APIs and Control Flow
`TestIsMinTTY` creates named pipes with pty-master and ordinary pipe names, then asserts `CanUpdateStatus` returns true only for the pty form. Control flow uses Windows named-pipe creation and closes handles after assertions.

## State, Persistence, Dependencies, and Integration
State is OS pipe handles. Dependencies are Windows syscalls and shared test helpers.

## Risks and Test Signals
The test catches regressions in filename pattern detection but not native console cursor movement.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows_test.go -->
