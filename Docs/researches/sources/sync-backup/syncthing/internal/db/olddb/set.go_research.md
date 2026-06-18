# sources/sync-backup/syncthing/internal/db/olddb/set.go

## Purpose
This file provides a small legacy file-set abstraction for reading old database file sequences with native filename conversion.

## Important APIs, Control Flow, And State
`deprecatedFileSet` stores a folder string and low-level database reference. `Iterator` is a callback receiving `protocol.FileInfo`. `NewFileSet` constructs the wrapper. `Snapshot` opens a read-only transaction and stores the folder. `Snapshot.Release` closes the transaction. `WithHaveSequence(startSeq, fn)` iterates sequence-indexed files from the snapshot transaction and wraps the callback with `nativeFileIterator`, which converts file names through `osutil.NativeFilename` before yielding.

## State And Persistence
No new persistence is introduced; snapshots read old database state. Runtime state is the active read-only transaction.

## Dependencies And Integration Points
It depends on `osutil` and `protocol`. It integrates with olddb transaction code and migration paths that need sequence-ordered local file metadata in native path form.

## Risks And Test Signals
Callers must release snapshots. The abstraction only exposes sequence iteration in this subset. Tests should verify snapshot release, sequence start behavior, native filename conversion, early callback termination, and error propagation from the transaction.
