# sources/storage-engines/badger/txn.go

## Purpose
This file implements Badger transactions and the oracle that assigns timestamps, tracks pending reads/writes, detects conflicts, and provides serializable snapshot isolation for normal mode plus timestamp control for managed mode.

## Important APIs, Types, and Functions
- `oracle` tracks `nextTxnTs`, read and transaction watermarks, discard timestamp, committed transaction conflict keys, and locks for timestamp/write-channel ordering.
- `newOracle`, `readTs`, `newCommitTs`, `doneRead`, `doneCommit`, `discardAtOrBelow`, and cleanup methods manage MVCC timestamps and conflict history.
- `Txn` stores read/commit timestamps, DB pointer, read fingerprints, conflict keys, pending writes, duplicate managed writes, iterator count, lifecycle flags, and size/count accounting.
- `pendingWritesIterator` overlays uncommitted writes for iterators in update transactions.
- Mutation APIs include `Set`, `SetEntry`, `Delete`, and internal `modify`.
- Read/lifecycle/commit APIs include `Get`, `Discard`, `Commit`, `CommitWith`, `ReadTs`, `NewTransaction`, `View`, and `Update`.

## Control Flow and State Behavior
In unmanaged mode, `oracle.readTs` assigns a snapshot timestamp as `nextTxnTs-1`, marks the read, and waits for all transactions up to that timestamp to finish writing. Update transactions track read key fingerprints for conflict detection and write key fingerprints for committed conflict history. `newCommitTs` runs conflict checks under oracle lock, assigns or uses commit timestamps, begins transaction watermark tracking, and records committed conflict keys when enabled.

`Txn.modify` validates writeability, lifecycle, key/value sizes, banned prefixes, DB bans, and batch size limits; then records conflict keys and stores the entry in `pendingWrites`, preserving duplicate versions in managed mode. `Get` first checks pending writes for read-your-own-write behavior, then records read keys for update transactions and queries `db.get` at `KeyWithTs(key, readTs)`.

`commitAndSend` serializes commit timestamp assignment with write-channel submission, appends timestamp suffixes to keys, adds transaction markers when all writes share one timestamp, sends entries to the write channel, and returns a callback that waits for durability before marking the commit timestamp done. `Commit` blocks on that callback; `CommitWith` runs it asynchronously.

## Dependencies and Integration Points
Transactions integrate with DB write channel, value log/LSM writes, iterators, key timestamp helpers, oracle watermarks, managed transaction APIs, conflict detection, and compaction discard timestamps. They depend on `y.WaterMark`, `z.Closer`, `z.MemHash`, Badger errors, and internal meta bits such as `bitTxn`, `bitFinTxn`, and `bitDelete`.

## Risks and Edge Cases
The transaction object itself is not thread-safe except for read-key tracking needed by multiple iterators. Failing to call `Discard` can hold read watermarks and delay discard/compaction. Managed mode requires `CommitAt`/explicit timestamps; committing timestamp zero with transaction markers is rejected. Conflict detection uses hashed keys, so theoretical hash collisions can cause false conflicts. `CommitWith` callbacks run in goroutines and must handle errors.

## Test Signals
This subset does not include `txn_test.go`, but many stream writer tests exercise transactions after restore, managed timestamp setup, deletes, writes, and oracle reinitialization. Broader Badger tests likely cover SSI and iterator integration.
