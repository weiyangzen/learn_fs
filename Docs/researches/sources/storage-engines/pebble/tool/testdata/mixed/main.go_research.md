# Research: sources/storage-engines/pebble/tool/testdata/mixed/main.go

## Purpose
`tool/testdata/mixed/main.go` generates a fixture database containing both point keys and range keys, with one flushed SSTable and one unflushed memtable represented in the WAL. The fixture is designed for CLI tests that inspect mixed point/range-key content across SSTables and WALs.

## Important APIs, Types, And Functions
`main` removes prior generated files under `./tool/testdata/mixed` while preserving `main.go`, opens Pebble with `testkeys.Comparer`, `FormatNewest`, logging event listener, and disabled automatic compactions, then writes two batches. Local closures wrap `Batch.Set`, `RangeKeySet`, `RangeKeyUnset`, and `RangeKeyDelete`.

## Control Flow
The first batch writes 26 alpha point keys at sequence-style suffix `@1`, a range key set over `[a,z)`, a range key unset over `[a,z)`, and a range key delete over `[a,b)`. It commits and flushes, producing an SSTable. The second batch writes a later point key and additional range key operations but does not flush, leaving data in the memtable/WAL when the process exits.

## State And Persistence
The generator mutates the fixture directory by deleting old generated files and writing a Pebble DB. Persistent artifacts include the table file, WAL, manifest marker, lock/options files, and related metadata. It intentionally leaves unflushed state so WAL introspection has content.

## Dependencies And Integration Points
It integrates Pebble batch APIs, range-key APIs, `internal/testkeys` deterministic key formatting, and `vfs.Default`. The output is consumed by `tool` datadriven tests that need predictable range key and point key layout.

## Risks And Edge Cases
The cleanup walk removes any file except `main.go` and directories under `outDir`, so the path must be correct. Not closing the DB explicitly means process exit handles cleanup; if future Pebble behavior requires close for durability of some artifacts, the fixture contract may need adjustment. Range bounds use `[a,z)`, so the last generated alpha key and range end semantics are intentionally exclusive.

## Test Signals
Signals include one SSTable with flushed point and range keys, one WAL with unflushed point and range-key mutations, testkey formatting stability, and command output for range key set/unset/delete records.
