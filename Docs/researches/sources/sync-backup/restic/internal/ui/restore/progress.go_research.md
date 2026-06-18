<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress.go -->
# sources/sync-backup/restic/internal/ui/restore/progress.go

## Purpose
Tracks restore progress state and coordinates periodic/final restore progress printing.

## Important APIs and Control Flow
`State`, `Progress`, `ProgressPrinter`, `ItemAction` constants, `NewProgress`, `newProgress`, `update`, `AddFile`, `AddProgress`, `AddSkippedFile`, `ReportDeletion`, `Error`, and `Finish` are central. It records per-file partial progress to avoid double-counting and emits completed item events once total bytes are reached. Control flow creates an updater using UI interval rules, updates state under a mutex, adds skipped/deleted counters immediately, proxies errors to the printer, and stops with a final summary in `Finish`.

## State, Persistence, Dependencies, and Integration
State includes progress map, aggregate counters, start time, printer, and updater goroutine. Integration is with `Restorer` and `fileRestorer` progress callbacks.

## Risks and Test Signals
Risks include double-counting repeated blob updates, missing completion events for zero-size items, and races with concurrent restore workers. Tests cover add/progress/finish/error/skipped/deleted/action behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress.go -->
