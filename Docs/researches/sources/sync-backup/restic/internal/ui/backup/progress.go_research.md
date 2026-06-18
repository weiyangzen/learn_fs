<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress.go -->
# sources/sync-backup/restic/internal/ui/backup/progress.go

## Purpose
Tracks backup progress state and feeds periodic updates to a backup progress printer.

## Important APIs and Control Flow
`ProgressPrinter`, `Counter`, `Progress`, `NewProgress`, `newProgress`, `Error`, `StartFile`, `CompleteBlob`, `CompleteItem`, `ReportTotal`, and `Finish` are central. `Progress` protects state with a mutex and embeds `progress.Updater` for timed/signal updates. Control flow starts updates only after scanning begins, estimates remaining seconds after scan completion using `rateEstimator`, tracks current files, increments processed file/dir/blob counters, maps archiver previous/current nodes to new/unchanged/modified item messages, and stops the updater before final summary.

## State, Persistence, Dependencies, and Integration
State includes start time, rate estimator buckets, scan flags, current file set, counters, error count, and printer. Dependencies include archiver/data node stats and UI progress infrastructure.

## Risks and Test Signals
Risks include races in concurrent archiver callbacks, inaccurate remaining-time estimates, and stale current-file entries after errors. Tests exercise state transitions for files, dirs, blobs, errors, totals, and finish behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress.go -->
