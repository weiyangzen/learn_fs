<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text.go -->
# sources/sync-backup/restic/internal/ui/restore/text.go

## Purpose
Implements human-readable restore progress output.

## Important APIs and Control Flow
`textPrinter` implements `Update`, `Error`, `CompleteItem`, and `Finish` using UI formatting helpers and verbosity-aware terminal printing. Control flow builds a single status line with duration, percent, files/dirs, byte totals, skipped and deleted counts; complete-item output maps restore actions to readable verbs; finish clears status and prints success or partial summary.

## State, Persistence, Dependencies, and Integration
State is terminal reference. Dependencies are UI byte/percent/duration formatters and generic terminal printer behavior.

## Risks and Test Signals
Risks are formatting drift and output that is hard to scan for large paths. Tests assert status, summaries, skipped output, complete-item text, and error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text.go -->
