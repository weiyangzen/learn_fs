# sources/storage-engines/rocksdb/examples/transaction_example.cc

## Purpose
`transaction_example.cc` demonstrates RocksDB's pessimistic `TransactionDB` API, including lock-based conflict prevention, snapshot reads, `GetForUpdate`, savepoints, rollback, and commit behavior.

## Important APIs and control flow
The example opens `TransactionDB` with `TransactionDBOptions` and runs three scenarios. The first starts a transaction, writes `"abc"`, shows outside reads cannot see the uncommitted value, writes unrelated `"xyz"` outside, then attempts an outside write to `"abc"` that fails with `Status::kLockTimeout` because the transaction holds the key lock. Commit succeeds and `"abc"` becomes visible.

The second starts with `set_snapshot=true`, writes `"abc"` outside, reads latest committed value without snapshot, reads old value with snapshot, then `GetForUpdate()` on the snapshotted key returns `Busy`, after which the transaction rolls back. The third uses multiple snapshots and a savepoint: it writes `"x"`, observes outside `"y"`, advances the transaction snapshot, updates `"y"`, rolls back to the savepoint, commits, and verifies `"x"` is committed while `"y"` remains at the outside value.

## State, persistence, and integration
The DB is a fixed temp path and is destroyed at the end. Integration points are `TransactionDB`, `Transaction`, `TransactionOptions`, `Snapshot`, savepoint APIs, and standard read/write options.

## Risks and test signals
Manual transaction and DB deletion can leak on assertion failure. Snapshot pointers in `ReadOptions` are explicitly cleared after transaction deletion, which is required. The example depends on default lock timeout behavior for `kLockTimeout`. Test signals are expected lock timeout for outside conflicting write, expected busy status for snapshot `GetForUpdate`, rollback to savepoint preserving outside `"y"`, and clean destroy.
