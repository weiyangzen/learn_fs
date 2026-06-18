# sources/storage-engines/pebble/flush_test.go

## Purpose
Provides focused tests for manual and asynchronous flushing, plus edge cases where flushed keys or range tombstone boundaries are empty byte slices. It validates that flushes update the current version and that empty keys are treated as real keys rather than nil sentinels.

## Important APIs, Types, And Functions
`TestManualFlush` drives `DB.Flush`, `DB.AsyncFlush`, `DB.NewBatch`, `Batch.Commit`, `runBatchDefineCmd`, and version string rendering through a datadriven file. `TestFlushDelRangeEmptyKey` writes `DeleteRange([]byte{}, "z")` then flushes. `TestFlushEmptyKey` writes `Set(nil, "hello")`, flushes, and reads the empty key through `Get`.

## Control Flow
`TestManualFlush` opens a DB with automatic compactions disabled and uses datadriven commands: `batch` builds and commits a batch, `flush` synchronously flushes and prints the current version, `async-flush` captures the current version, starts `AsyncFlush`, waits until the version pointer changes, and prints the new version, and `reset` reopens the DB. The empty-key tests perform direct DB operations and close after verification.

## State And Persistence Behavior
Flushes move mutable memtable contents into SSTables and update the version set/manifest state. The tests inspect the in-memory current version string after flushes and rely on persisted SST contents for `Get(nil)` after `Flush`. The range-delete empty-start case ensures an empty start key survives flush encoding and ordering invariants.

## Dependencies And Integration Points
The file depends on datadriven testdata, `vfs.NewMem`, `try` polling, DB version state under `d.mu`, batch command helpers, and public DB APIs. It integrates with flush scheduling, memtable rotation, version edit application, range tombstone flushing, and point lookup.

## Risks And Edge Cases
Manual and async flush behavior may regress if flush scheduling reports completion before a version update or if automatic compactions interfere with expected version strings. Empty keys are especially risky because nil and empty slices can be conflated in Go; these tests guard range deletion and point key invariant code against that confusion.

## Test Signals
Datadriven output from `testdata/manual_flush` is the main signal for version layout. Additional signals are successful flush/close without invariant failures, `Get(nil)` returning `hello`, and leaktest completion.
