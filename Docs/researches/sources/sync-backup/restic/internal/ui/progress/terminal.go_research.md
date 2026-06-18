<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/terminal.go -->
# sources/sync-backup/restic/internal/ui/progress/terminal.go

## Purpose
Adapts the generic progress printer interface to a real UI terminal.

## Important APIs and Control Flow
`CalculateProgressInterval`, `newProgressMax`, `terminalPrinter`, and `NewTerminalPrinter` handle update cadence, progress counter creation, terminal-only counters, errors/status/print output, and verbosity levels. Control flow disables periodic status for quiet output, uses JSON-aware behavior to avoid mixed terminal status, and routes `E`, `S`, `PT`, `P`, `V`, and `VV` according to verbosity and terminal capabilities.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies include core restic counters, UI terminal abstraction, and `progress.Counter`.

## Risks and Test Signals
Risks are noisy output in JSON mode, incorrect interval choices, and verbosity regressions. Tests for backup/restore printers and updater/counter cover the main integration paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/terminal.go -->
