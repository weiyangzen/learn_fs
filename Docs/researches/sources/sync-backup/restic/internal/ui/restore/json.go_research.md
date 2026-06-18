<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json.go -->
# sources/sync-backup/restic/internal/ui/restore/json.go

## Purpose
Implements JSON progress output for restore operations.

## Important APIs and Control Flow
`jsonPrinter` implements restore `ProgressPrinter`: `Update`, `Error`, `CompleteItem`, and `Finish`. It emits JSON `status`, `error`, `verbose_status`, and `summary` objects. Control flow maps restore `State` fields to JSON counters, computes percent when total bytes are known, maps `ItemAction` values to actions, suppresses verbose item messages below verbosity 3, and emits restore errors as non-fatal JSON errors.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies are UI JSON formatting and generic progress terminal printing.

## Risks and Test Signals
Risks are JSON schema drift and panics on unknown item actions. Tests cover update, skipped files, summaries, complete-item actions, and error JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json.go -->
