# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_external_pthread.h

## Purpose
`toku_external_pthread.h` adapts RocksDB `TransactionDBMutexFactory` mutexes and condition variables to the TokuDB-style external mutex/cond API used for interruptible lock waits.

## Important APIs, Types, And Functions
Aliases define `toku_external_mutex_factory_t`, `toku_external_mutex_t`, and `toku_external_cond_t` as shared pointers to RocksDB mutex/cond types. Inline functions create/destroy, lock/unlock, signal/broadcast, timed wait, and trylock external mutexes/conditions.

## Control Flow
Initialization allocates a RocksDB mutex or condvar from the factory. Timed wait calls `TransactionDBCondVar::WaitFor()` and maps OK to `0`, anything else to `ETIMEDOUT`. `trylock` currently calls blocking `Lock()` and returns `0`.

## State And Persistence Behavior
State is shared-pointer ownership of RocksDB synchronization objects. No persistent state is involved.

## Dependencies
It includes pthread/time headers, RocksDB transaction DB mutex interfaces, and portability macros.

## Integration Points
`lock_request` uses external conditions for potentially long waits so RocksDB can provide custom wait primitives. `lt_lock_request_info` uses external mutexes around pending waiter lists.

## Risks And Edge Cases
`toku_external_mutex_trylock()` is not a true trylock in this port; callers expecting non-blocking behavior may block. The factory pointer must be valid and able to allocate both mutexes and condition variables. Timed-wait error mapping loses error detail.

## Test Signals
Wait timeout, waiter wakeup, killed waiter, and custom `TransactionDBMutexFactoryImpl` tests exercise this wrapper.
