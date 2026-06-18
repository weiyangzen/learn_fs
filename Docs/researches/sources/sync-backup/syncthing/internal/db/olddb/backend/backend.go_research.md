# sources/sync-backup/syncthing/internal/db/olddb/backend/backend.go

## Purpose
This file defines the legacy database backend abstraction used for read-only access to old Syncthing LevelDB databases during migration or compatibility operations.

## Important APIs, Control Flow, And State
It defines `CommitHook`, `Reader`, `Writer`, `ReadTransaction`, `WriteTransaction`, `Iterator`, and `Backend`. `Reader` supports key lookups and prefix/range iterators. `WriteTransaction` describes legacy writable transaction behavior, including `Checkpoint` and `Commit`, although the current LevelDB reader implementation is read-only. `IsClosed` and `IsNotFound` normalize sentinel errors. `releaser` wraps a close wait group with `sync.Once`, and `closeWaitGroup` prevents new operations after `CloseWait` while waiting for active snapshots to release.

## Dependencies And Integration Points
It depends on `errors` and `sync`. The LevelDB backend implements these interfaces. Legacy olddb code uses `Backend` and `ReadTransaction` to traverse old keys and reconstruct file metadata.

## Risks And Test Signals
The transaction documentation is broader than the read-only implementation in this subset, so maintainers must check concrete backend support before assuming writes exist. Correct close behavior depends on all transactions and iterators being released. Tests should cover `IsClosed`, `IsNotFound`, idempotent release, and `CloseWait` blocking until live readers finish while rejecting new readers.
