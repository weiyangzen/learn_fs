# sources/sync-backup/syncthing/internal/db/olddb/backend/leveldb_open.go

## Purpose
This file opens legacy Syncthing LevelDB databases in read-only mode.

## Important APIs, Control Flow, And State
`OpenLevelDBRO(location)` constructs LevelDB options with `OpenFilesCacheCapacity` set to `dbMaxOpenFiles` and `ReadOnly` set to true, opens the database through `open`, and wraps it in `newLeveldbBackend`. `open` is a small seam around `leveldb.OpenFile`.

## Dependencies And Integration Points
It depends on goleveldb `leveldb` and `opt`. It integrates with olddb migration/read paths that need to inspect existing databases without modifying them.

## Risks And Test Signals
The file is intentionally small, but operational risk lies in read-only opening failing on corrupted or locked LevelDBs. The open-file cache is fixed at 100. Tests should cover opening a valid DB, missing path errors, read-only enforcement, and propagating LevelDB open errors.
