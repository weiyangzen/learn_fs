# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.h

## Purpose
`locktree.h` declares the central range-lock abstractions: a manager for all dictionary locktrees, a per-dictionary `locktree`, pending request metadata, status counters, and callback contracts for create/destroy/escalation.

## Important APIs, Types, And Functions
Key types include `DICTIONARY_ID`, `lt_counters`, `lt_lock_request_info`, callback typedefs, `locktree_manager`, and `locktree`. Manager APIs cover lifecycle, memory limit, get/release/reference, status, pending iteration, memory accounting, escalation, and waiter killing. `locktree` APIs cover lifecycle, acquisition, conflict discovery, release, escalation, comparator/barrier setup, status dump, and userdata.

## Control Flow
The header documents manager ownership: callers get a referenced locktree by dictionary ID and later release it; the manager destroys it on final release. Lock acquisition returns immediately with success, `DB_LOCK_NOTGRANTED`, or out-of-locks, while `lock_request` handles waits.

## State And Persistence Behavior
Manager state includes global lock-memory limit/current usage, cumulative counters, callbacks, OMT map, mutexes, and escalator state. `locktree` state includes dictionary ID, comparator, concurrent range tree, pending request info, STO buffer/score, and escalation barrier. All state is process-local.

## Dependencies
It includes atomic support, DBT/status definitions, comparator, external/internal pthread wrappers, time helpers, OMT, `range_buffer`, `txnid_set`, and wait graph declarations.

## Integration Points
This is the imported locktree interface wrapped by RocksDB's `RangeTreeLockManager`. Status and escalation functions feed public range-lock manager handle methods tested in `range_locking_test.cc`.

## Risks And Edge Cases
Reference counting is external and not RAII. Comparator lifetime is guaranteed by higher layers. STO and normal tree lock lists duplicate transaction-owned lock tracking, and comments flag this as a layering issue. `set_max_lock_memory()` rejects lowering below current usage.

## Test Signals
Manager lifecycle, memory limit/escalation, lock acquire/release, pending request iteration, status reporting, and reference-count races are the intended test surfaces.
