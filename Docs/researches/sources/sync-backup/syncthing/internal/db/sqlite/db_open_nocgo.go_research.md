# sources/sync-backup/syncthing/internal/db/sqlite/db_open_nocgo.go

## Purpose
This build-tagged file selects the pure-Go SQLite driver for non-cgo, non-wazero builds.

## Important APIs and Control Flow
Under `//go:build !cgo && !wazero`, it side-effect imports `modernc.org/sqlite`, sets `dbDriver = "sqlite"`, and uses `_pragma` DSN options for foreign keys, recursive triggers, synchronous mode, and immediate transaction locking. Its `init` function records the `modernc-sqlite` build tag through `build.AddTag`.

## State and Persistence Behavior
The constants shape all SQLite connections in this build mode. The driver choice also affects behavior around URI parsing, locking, and pragma support.

## Dependencies and Integration Points
It integrates with `basedb.go` connection setup and Syncthing build metadata. It is mutually exclusive with the cgo driver file.

## Risks and Test Signals
The main risk is semantic drift from the cgo driver. The test suite's path special-character, concurrency, foreign-key, trigger, and migration behaviors are relevant for both driver variants.
