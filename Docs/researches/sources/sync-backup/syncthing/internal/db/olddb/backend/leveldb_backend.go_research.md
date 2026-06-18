# sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_backend.go

## Purpose
This file implements the legacy `backend.Backend` read API on top of goleveldb.

## Important APIs, Control Flow, And State
`leveldbBackend` holds a `*leveldb.DB`, a close wait group, and location string. `NewReadTransaction` creates a LevelDB snapshot through `newSnapshot`; snapshots acquire a releaser so `Close` can wait for them. Backend-level `Get`, `NewPrefixIterator`, and `NewRangeIterator` delegate to LevelDB. `leveldbSnapshot` exposes the same read methods against a stable snapshot and releases both snapshot and waitgroup slot in `Release`. `leveldbIterator.Error` wraps LevelDB iterator errors into backend sentinel errors.

## State And Persistence
Persistent state is the existing LevelDB database. This wrapper is read-only at the abstraction level in this repository path; it does not manage writes. Runtime state tracks live snapshots for safe close.

## Dependencies And Integration Points
It depends on `github.com/syndtr/goleveldb/leveldb`, iterators, and util ranges. It is constructed by `OpenLevelDBRO` and consumed by legacy olddb readers.

## Risks And Test Signals
Backend prefix/range iterators created directly on `leveldbBackend` are not tracked by `closeWG`, unlike snapshots, so callers should avoid closing concurrently with active direct iterators. Snapshot iterators must be released before releasing the snapshot. Tests should cover not-found/closed error mapping, snapshot consistency, range boundaries, prefix scans, and closing with live snapshots.
