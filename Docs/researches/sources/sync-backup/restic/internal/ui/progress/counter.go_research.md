<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter.go -->
# sources/sync-backup/restic/internal/ui/progress/counter.go

## Purpose
Implements a concurrency-safe progress counter backed by the shared updater goroutine.

## Important APIs and Control Flow
`Counter` embeds `Updater`, stores atomic value/max fields, and implements `restic.Counter`. `NewCounter` wires an update callback that reads `Get`; `Add`, `SetMax`, `Get`, and inherited `Done` are safe for concurrent callers. Control flow reports periodically or on signals via `Updater`, and performs a final callback on `Done`.

## State, Persistence, Dependencies, and Integration
State is in-memory atomic counters and updater goroutine state. It integrates core restic counters with UI progress rendering.

## Risks and Test Signals
Risks are goroutine leaks if `Done` is not called and races around final reporting. Tests cover increment/max/report behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter.go -->
