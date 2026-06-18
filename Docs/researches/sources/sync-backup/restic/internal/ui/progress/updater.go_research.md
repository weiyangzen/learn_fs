<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater.go -->
# sources/sync-backup/restic/internal/ui/progress/updater.go

## Purpose
Runs periodic and signal-triggered progress callbacks.

## Important APIs and Control Flow
`Updater`, `UpdateFunc`, `NewUpdater`, `Done`, and `run` manage a goroutine, optional ticker, stop/stopped channels, runtime measurement, and SIGUSR1/SIGINFO-triggered reports. Control flow selects between ticker, progress signal channel, and stop; `Done` stops the ticker, closes the stop channel, waits for the final callback, and is idempotent for later calls.

## State, Persistence, Dependencies, and Integration
State is goroutine/channel/ticker state and start time. Dependencies include `internal/ui/signals` and debug logging.

## Risks and Test Signals
Risks are goroutine leaks, double-close panics, and final-update races. Tests cover normal updates, double `Done`, and no-tick operation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater.go -->
