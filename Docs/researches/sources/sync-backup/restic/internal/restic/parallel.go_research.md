<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel.go -->
# sources/sync-backup/restic/internal/restic/parallel.go

## Purpose
Provides concurrency helpers for listing repository files and deleting unpacked repository files.

## Important APIs and Control Flow
`ParallelList` streams `Lister.List` output into worker goroutines under an `errgroup`; `ParallelRemove` uses a generic `RemoverUnpacked` repository, limits goroutines to `repo.Connections()`, reports per-ID results, and advances a `Counter` only on successful removal. Both helpers derive a cancellable context from `errgroup.WithContext`, so the first worker error cancels pending producers/workers. `ParallelRemove` also stops scheduling when cancellation is observed.

## State, Persistence, Dependencies, and Integration
State is transient goroutine, channel, and progress-counter state. Integration points are repository listers/removers, `IDSet`, `FileType` generics, `debug.Log`, and `golang.org/x/sync/errgroup`.

## Risks and Test Signals
Risks are deadlock/cancellation regressions, accidental progress increments on failed deletes, and loop-variable capture in concurrent removal. Tests cover successful removes, remove/report errors, reporting IDs, progress count, and cancellation-sensitive scheduling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel.go -->
