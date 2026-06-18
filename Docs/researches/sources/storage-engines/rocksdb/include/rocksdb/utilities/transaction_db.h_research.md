# sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db.h

## Purpose
Pessimistic transaction DB wrapper and configuration surface, including lock managers, deadlock reporting, write policies, timestamped snapshots, secondary indices, and write optimizations.

## Important APIs, Types, And Functions
Defines `TxnDBWritePolicy`, `LockManagerHandle`, `RangeLockManagerHandle`, `NewRangeLockManager`, `TransactionDBOptions`, `TransactionOptions`, `TransactionDBWriteOptimizations`, lock/deadlock structs, and `TransactionDB`. Key DB methods include optimized `Write`, direct `DeleteRange` rejection, `Open`, `PrepareWrap`, `WrapDB`, `WrapStackableDB`, `BeginTransaction`, prepared transaction lookup, lock/deadlock status, and timestamped snapshot APIs.

## Control Flow, State, And Persistence
Open wraps a base DB and installs transaction locking. Transactions acquire locks on updates and `GetForUpdate`; direct writes may use optimization hints. Timestamped snapshots are tracked in the DB wrapper. Write-prepared/unprepared policies can persist prepared or uncommitted state that must be recovered, committed, or rolled back.

## Dependencies And Integration Points
Depends on `DB`, `Comparator`, `StackableDB`, `Transaction`, `SecondaryIndex`, and custom mutex factories. Integrates with lock tables, range locking, WAL recovery, MyRocks compatibility options, secondary-index maintenance, and large transaction optimizations.

## Risks And Edge Cases
Experimental write policies have compatibility caveats. Negative lock timeouts can block indefinitely. Forgotten transactions can retain locks unless expiration is set. Skipping concurrency control depends entirely on application correctness. Large transaction memtable bypass is experimental and unsupported for merges/entities. Direct transactional `DeleteRange` is not supported outside constrained optimized `Write`.

## Test Signals
Cover lock timeouts, deadlock buffers, range locks/escalation, expiration, prepared recovery, write policies, optimized writes, `DeleteRange` rejection, timestamped snapshots, secondary indices, custom mutex factories, and large-transaction bypass.
