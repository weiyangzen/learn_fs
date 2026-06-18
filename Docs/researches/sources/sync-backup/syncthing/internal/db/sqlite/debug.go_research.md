# sources/sync-backup/syncthing/internal/db/sqlite/debug.go

## Purpose
This file registers the SQLite database package with Syncthing's structured logging utilities.

## Important APIs and Control Flow
The package-level `init` calls `slogutil.RegisterPackage("SQLite database")`.

## State and Persistence Behavior
It has no database or filesystem persistence. Its only state effect is process-global logging package registration during package initialization.

## Dependencies and Integration Points
It depends on `internal/slogutil`. The debug and service files emit structured logs that benefit from this package registration.

## Risks and Test Signals
The risk is minimal. Removing or renaming the registration could affect log filtering or diagnostics, but not database correctness. There are no direct tests.
