<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text.go -->
# sources/sync-backup/restic/internal/ui/backup/text.go

## Purpose
Implements human-readable backup progress output.

## Important APIs and Control Flow
`textProgress` implements `ProgressPrinter` with terminal status lines, verbose item output, scanner/archive errors, totals, summaries, and reset behavior. Control flow formats bytes, percentages, durations, current files, and summary counts; verbosity controls detailed per-item output through the embedded terminal printer.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity through `progress.NewTerminalPrinter`. It depends on UI formatting helpers, archiver stats, restic IDs, and terminal status capability.

## Risks and Test Signals
Risks are formatting regressions and output that does not fit terminal widths. Tests cover scanner/archive error strings, while progress and formatting tests cover related state/format helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text.go -->
