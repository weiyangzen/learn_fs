# sources/sync-backup/syncthing/internal/db/sqlite/util.go

## Purpose
This file provides shared SQLite utility types for row iteration, version-vector SQL conversion, indirect FileInfo reconstruction, and prefix range construction.

## Important APIs and Control Flow
`iterStructs[T]` converts `sqlx.Rows` into a Go iterator, `StructScan`s each row into `T`, optionally calls `cleanup()`, closes rows on exit, and exposes scan/row errors through a returned function. `dbVector` implements `driver.Valuer` and `sql.Scanner` for `protocol.Vector` strings and sorts counters after scanning to repair older serialization ordering. `indirectFI.FileInfo` unmarshals a stored BEP `FileInfo`, optionally unmarshals an external `dbproto.BlockList` into its `Blocks`, converts the name to native format, and returns a `protocol.FileInfo`. `prefixEnd` increments the final non-0xff byte to make a lexicographic exclusive upper bound.

## State and Persistence Behavior
The file itself is stateless, but defines how version vectors and FileInfo payloads are serialized/deserialized from persisted database columns.

## Dependencies and Integration Points
It depends on `sqlx`, `database/sql/driver`, generated `bep` and `dbproto`, `proto`, `osutil`, and `protocol`. It is used by nearly all folder query files.

## Risks and Test Signals
`prefixEnd` panics on empty prefixes and does not handle all-0xff overflow specially. `dbVector.Scan` expects strings only. `util_test.go` covers vector round trip; prefix behavior is heavily exercised through database prefix tests.
