<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/managed_db.go -->
# sources/storage-engines/badger/managed_db.go

## Purpose
This file exposes Badger's managed timestamp mode for systems that need external control over read and commit timestamps.

## Important APIs, Types, And Functions
`OpenManaged` sets `Options.managedTxns` and calls `Open`. `DB.NewTransactionAt` creates a transaction with a caller-supplied read timestamp. `DB.NewWriteBatchAt` creates a managed write batch with fixed commit timestamp. `DB.NewManagedWriteBatch` creates a write batch that accepts per-entry timestamps. `Txn.CommitAt` commits at a supplied timestamp, optionally using an async callback. `DB.SetDiscardTs` tells the oracle the timestamp at or below which invalid/deleted versions may be discarded.

## Control Flow
All managed APIs panic if `db.opt.managedTxns` is false. `NewTransactionAt` starts a normal internal transaction and overwrites `readTs`. `NewWriteBatchAt` sets both `WriteBatch.commitTs` and the underlying transaction commit timestamp. `CommitAt` sets `txn.commitTs`, then either calls synchronous `Commit` or asynchronous `CommitWith`.

## State And Persistence Behavior
Managed mode changes transaction timestamp assignment and compaction discard eligibility. Writes still flow through the normal write path, WAL/value log, memtable, LSM, and manifest machinery. `SetDiscardTs` affects future compaction decisions and value-log reclaimability, not immediate deletion by itself.

## Dependencies And Integration Points
The file integrates with `Open`, `DB.newTransaction`, `DB.newWriteBatch`, `Txn.Commit`, `Txn.CommitWith`, write batch internals, and the transaction oracle. It is used by Dgraph-style callers and heavily by tests that need deterministic versions.

## Risks And Edge Cases
Panic-on-wrong-mode makes API misuse fail loudly. External callers must guarantee timestamp monotonicity and conflict semantics; Badger will use the supplied timestamps. Async `CommitAt` returns nil after scheduling `CommitWith`, so commit failures arrive only through the callback. Incorrect discard timestamps can make compaction drop versions still needed by external readers.

## Test Signals
`managed_db_test.go` covers managed drop-all/drop-prefix, write batches with fixed and per-entry timestamps, duplicate version handling, and value-log discard stat resets. `levels_test.go` uses managed mode to validate compaction version retention.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/managed_db.go -->
