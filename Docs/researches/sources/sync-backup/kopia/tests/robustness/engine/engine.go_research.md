
# sources/sync-backup/kopia/tests/robustness/engine/engine.go

## Purpose
Constructs and manages the robustness test engine, tying together metadata persistence, snapshot repository, file writer, checker, logging, stats, initialization, and shutdown.

## Important APIs, Types, And Functions
- `Args` contains `MetaStore`, `TestRepo`, `FileWriter`, `WorkingDir`, and `SyncRepositories`; `Validate` enforces required fields.
- `New` creates an `Engine`, initializes run stats, sets up logging, creates a `checker.Checker`, and configures recovery mode.
- `Engine` stores interfaces, checker, cleanup routines, run/cumulative stats, engine log, and mutexes.
- `Shutdown` optionally takes a final snapshot after writes, prints summary, saves logs/stats/snapshot index, flushes metadata, and runs cleanup.
- `setupLogging`, `formatLogName`, `cleanComponents`, and `Init` handle log file setup, cleanup, and persisted metadata loading/reconciliation.

## Control Flow
Engine construction validates dependencies, opens a new persistent log file under the metadata store directory, then creates the checker. `Init` loads persisted metadata, stats, logs, and snapshot index before verifying metadata against the repository. `Shutdown` inspects current-run logs to decide whether a final snapshot is needed, persists state, flushes metadata, and cleans components.

## State And Persistence Behavior
Persists engine logs, stats, and snapshot ID index through `MetaStore`. Also writes a log file to the metadata persist directory and mutates snapshot repository state through final snapshots. Cleanup removes temp restore/file-writer resources via registered cleanup routines.

## Dependencies And Integration Points
Uses `robustness.Persister`, `robustness.Snapshotter`, `robustness.FileWriter`, `checker.NewChecker`, `internal/clock`, and engine log/stats methods defined elsewhere in the package.

## Risks And Edge Cases
`log.SetOutput` is global, so parallel engine tests can interfere with logging. `Shutdown` ignores errors from the final snapshot action. Cleanup runs via defer after persistence; errors before cleanup can still leave external resources if cleanup routines fail.

## Test Signals
Provides lifecycle and persistence backbone for robustness tests, especially restart/recovery behavior.
