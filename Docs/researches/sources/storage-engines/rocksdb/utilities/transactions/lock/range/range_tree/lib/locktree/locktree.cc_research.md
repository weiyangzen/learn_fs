# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.cc

## Purpose
`locktree.cc` implements the core range-lock table for one dictionary/column family: immediate lock acquisition, conflict detection, shared read-lock coalescing, transaction lock release, lock dumping, single-transaction optimization, and escalation.

## Important APIs, Types, And Functions
Implemented public methods include `create()`, `destroy()`, reference counting, `acquire_read_lock()`, `acquire_write_lock()`, `get_conflicts()`, `release_locks()`, `escalate()`, userdata accessors, comparator/barrier setters, `dump_locks()`, and dictionary comparison.

Internal helpers include `row_lock`, overlap iteration, `determine_conflicting_txnids()`, memory accounting helpers, `sto_*` single-transaction optimization methods, `acquire_lock_consolidated()`, `remove_overlapping_locks_for_txnid()`, and escalation extraction/rebuild logic.

## Control Flow
Acquisition prepares the rangetree root, attempts STO fast path, then acquires the overlapping subtree. If an identical shared lock is the only overlap, the new owner is added. If overlaps all belong to the same txnid, ranges are merged into one dominating range. Otherwise conflict txnids are returned. Release iterates a transaction's range buffer and removes owned overlapping locks, exiting STO first for partial releases. Escalation locks the full tree, removes locks in batches, merges adjacent compatible locks unless a barrier is present, rebuilds the tree, and calls callbacks per txnid.

## State And Persistence Behavior
State is in-memory: comparator copy, reference count, concurrent tree pointer, userdata, pending request info, STO txnid/buffer/score, escalation barrier, and STO timing counters. Lock state is not persisted; higher layers track transaction-owned ranges separately.

## Dependencies
It depends on `concurrent_tree`, `range_buffer`, `growable_array`, memory macros, time helpers, OMT, transaction IDs, and the manager for memory accounting and callbacks.

## Integration Points
`lock_request` calls acquisition and conflict methods. `locktree_manager` creates, references, destroys, escalates, and reads status from locktrees. RocksDB range-lock manager wraps this object per column family/dictionary.

## Risks And Edge Cases
Memory accounting is approximate and must be balanced on every insert/remove/STO transition. Shared locks are supported only for identical ranges and are not merged during escalation. STO migration can create latency spikes, bounded by buffer size. Barriers must follow comparator ordering.

## Test Signals
Range conflict tests, shared-lock upgrade timeout, lock status dumping, wait counters, basic escalation, escalation barriers, and point-lock compatibility are key signals.
