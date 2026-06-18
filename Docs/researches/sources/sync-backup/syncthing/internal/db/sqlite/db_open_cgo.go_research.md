# sources/sync-backup/syncthing/internal/db/sqlite/db_open_cgo.go

## Purpose
This build-tagged file selects the cgo SQLite driver.

## Important APIs and Control Flow
Under `//go:build cgo`, it imports `github.com/mattn/go-sqlite3` for side-effect driver registration and sets `dbDriver = "sqlite3"`. `commonOptions` enables foreign keys, recursive triggers, synchronous mode, and immediate transaction locking using go-sqlite3 DSN parameters.

## State and Persistence Behavior
The file itself holds no runtime state, but its constants affect every `openBase` DSN in cgo builds. Foreign key and recursive trigger behavior are foundational to folder DB cascades and count triggers.

## Dependencies and Integration Points
It is consumed by `basedb.go` when opening `sqlx` connections. It is mutually exclusive with `db_open_nocgo.go`.

## Risks and Test Signals
The risk is DSN divergence between cgo and modernc builds. Any option mismatch can change transaction locking or trigger behavior. Database tests should be run under both build modes when touching these constants.
