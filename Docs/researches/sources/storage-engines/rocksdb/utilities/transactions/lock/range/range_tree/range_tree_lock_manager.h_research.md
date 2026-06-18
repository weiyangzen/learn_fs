# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.h

## Purpose
Declares the RocksDB range lock manager implementation that adapts Toku locktree to the `LockManager` and `RangeLockManagerHandle` interfaces.

## Important APIs, Types, And Functions
`RangeTreeLockManager` exposes column-family registration, deadlock buffer APIs, `TryLock`, unlock overloads, lock memory limits, status getters, point/range support flags, lock tracker factory access, `GetLockTreeForCF`, and escalation barrier configuration. It also declares endpoint serialization and wait callback helpers.

## Control Flow
The header defines the ownership model: locktrees are stored as `shared_ptr` values with a custom deleter that calls `locktree_manager::release_lt`; map access is guarded by `ltree_map_mutex_`; thread-local caches accelerate lookups.

## State And Persistence Behavior
Persistent storage is not involved. In-memory state includes the locktree manager, CF map, TLS cache, deadlock buffer, mutex factory, and escalation barrier function.

## Dependencies And Integration Points
Depends on RocksDB transaction lock manager interfaces and Toku locktree headers. The `RangeTreeLockTrackerFactory` returned here ensures transactions use range buffers that Toku can consume during release.

## Risks And Edge Cases
The class is compiled out on Windows. The no-op range-specific unlock overload means range release depends on tracker-based transaction cleanup. Users must call `AddColumnFamily` before locking a CF.

## Test Signals
Compile coverage verifies interface conformance. Runtime tests should verify factory creation, CF add/remove, memory-limit plumbing, deadlock buffer resizing, and tracker factory compatibility.
