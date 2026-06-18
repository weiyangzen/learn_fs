# sources/sync-backup/syncthing/internal/db/sqlite/util_test.go

## Purpose
This file tests `dbVector`, the SQLite conversion wrapper for `protocol.Vector`.

## Important APIs and Control Flow
`TestDbvector` creates a vector with two counters, wraps it as `dbVector`, calls `Value`, scans that value into another `dbVector`, and asserts the resulting vector equals the original.

## State and Persistence Behavior
The test does not open a database. It validates the serialization format that is stored in the `file_versions.version` column and later scanned back during global conflict resolution.

## Dependencies and Integration Points
It depends on `protocol.Vector`, `protocol.Counter`, and the `dbVector.Value`/`Scan` methods in `util.go`.

## Risks and Test Signals
This test catches basic scan/value breakage but not the older unsorted-counter repair path except indirectly if equality requires canonical ordering. `db_test.go` adds regression coverage for strange deleted-global behavior tied to vector ordering.
