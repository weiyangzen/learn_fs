<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater_test.go -->
# sources/sync-backup/restic/internal/ui/progress/updater_test.go

## Purpose
Tests updater lifecycle behavior.

## Important APIs and Control Flow
`TestUpdater` verifies callbacks happen and final reporting occurs; `TestUpdaterStopTwice` checks `Done` idempotence; `TestUpdaterNoTick` verifies an updater with zero interval still reports on final stop. Control flow uses short intervals and callback traces.

## State, Persistence, Dependencies, and Integration
State is local counters/channels in tests. Dependencies are the progress package and testing timeouts.

## Risks and Test Signals
The tests catch lifecycle regressions but cannot exhaustively prove timing behavior under scheduler delays.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater_test.go -->
