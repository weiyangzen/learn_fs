<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json.go -->
# sources/sync-backup/restic/internal/ui/backup/json.go

## Purpose
Implements JSON progress output for the backup command.

## Important APIs and Control Flow
`jsonProgress` embeds a terminal `progress.Printer` and implements `ProgressPrinter`: `Update`, `ScannerError`, `Error`, `CompleteItem`, `ReportTotal`, `Finish`, and `Reset`. It emits JSON `status`, `error`, `verbose_status`, and `summary` objects. Control flow formats status from total/processed counters, sorts current filenames for deterministic output, maps archiver item message types to JSON actions, suppresses verbose item output below verbosity 2, and renders final backup summary including snapshot ID and dry-run flag.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies are archiver stats, restic IDs, UI JSON formatting, and progress terminal printing.

## Risks and Test Signals
Risks are JSON contract drift and incorrect message-type mapping. Tests cover error and scanner-error JSON escaping; broader progress tests cover state feeding.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json.go -->
