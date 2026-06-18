<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_unix.go -->
# sources/sync-backup/restic/internal/terminal/terminal_unix.go

## Purpose
Selects terminal status update behavior on Unix.

## Important APIs and Control Flow
Unix implementations use POSIX clear/move helpers and terminal capability checks for whether status can be updated. Control flow is mostly platform dispatch around file descriptors and terminal detection.

## State, Persistence, Dependencies, and Integration
State is terminal display/cursor state. It integrates with UI progress printers that call `SetStatus`.

## Risks and Test Signals
Risks are redirected output and terminal detection mistakes; Windows has more specialized pipe detection tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_unix.go -->
