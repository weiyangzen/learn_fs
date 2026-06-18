# sources/storage-engines/tikv/components/raftstore/src/store/txn_ext.rs

## Purpose

Stores transaction-related in-memory extensions for a raftstore peer: max timestamp synchronization status after leadership changes and the peer's in-memory pessimistic lock table. It supports memory accounting, lock migration during split/merge/leader transfer, lock scanning for reads/diagnostics, and global metrics for pessimistic lock memory use.

## Important APIs, Types, And Functions

`TxnExt` contains `max_ts_sync_status` and `pessimistic_locks`. The timestamp sync status packs a synced bit, 31 bits of region epoch version, and 32 bits of raft term so stale PD update tasks cannot mark a newer leadership epoch as synced; `is_max_ts_synced` checks the low bit. `INSTANCE_MEM_SIZE` is a process-wide Prometheus gauge for pessimistic lock memory. `PeerPessimisticLocks` owns a `BTreeMap<Key, (PessimisticLock, bool)>`, a `LocksStatus`, raft `term`, region `version`, and per-peer `memory_size`. The bool marks locks that have a proposed but unapplied write deleting them.

`LocksStatus` distinguishes `Normal`, `TransferringLeader`, `MergingRegion`, `NotLeader`, and `IsInFlashback`. Public lock-table methods include `insert`, `remove`, `clear`, `is_empty`, `len`, `is_writable`, `get`, `get_mut`, `group_by_regions`, and `scan_locks`. `IntoIterator for &PeerPessimisticLocks` exposes map iteration. `Drop` subtracts remaining memory from the global gauge. `PessimisticLockPair` abstracts owned/borrowed insertion pairs and is implemented for `(Key, PessimisticLock)`.

## Control Flow

Insertion first computes incremental memory for keys not already present; overwrites do not add memory because the code assumes primary lock memory is stable for overwrite semantics. It rejects the entire input vector if the peer memory limit or global instance memory limit would be exceeded. After passing precheck, it inserts every lock with deleted flag false, updates peer memory, and increments the global gauge. `remove`, `clear`, and `Drop` subtract exactly the recorded key plus lock memory.

`group_by_regions` is used during region split. It requires regions sorted by start key, retains locks still belonging to the derived region, removes locks outside the derived range, clears their deleted marker, binary-searches the destination region by encoded key, moves them into corresponding new `PeerPessimisticLocks`, and transfers memory accounting from the original table to the returned tables. `scan_locks` performs a bounded BTree range scan over optional start/end keys, applies a caller filter, clones matching pessimistic locks into normal `Lock` values, and returns a `has_more` flag when the caller's limit is reached before the scan is exhausted.

## State And Persistence Behavior

All state is volatile peer memory. Pessimistic locks are not persisted here; they are part of raftstore peer runtime state and are coordinated through raft proposals, leadership changes, split/merge flows, and read snapshots. Memory accounting is explicit and mirrored in `INSTANCE_MEM_SIZE`, so every path that moves, removes, clears, or drops locks must keep gauge deltas balanced. The `LocksStatus` state gates writability and migration behavior during topology changes and flashback.

## Dependencies And Integration Points

Depends on `txn_types::{Key, Lock, PessimisticLock}`, kvproto `metapb::Region`, `parking_lot::RwLock`, and Prometheus. `TxnExt` is attached to peers and region snapshots, used by read workers for transactional extra operations, by PD worker max timestamp update tasks, and by peer FSM logic for leader transfer, split, merge, flashback, and applying proposed lock changes. `store/mod.rs` re-exports `LocksStatus`, `PeerPessimisticLocks`, `PessimisticLockPair`, and `TxnExt`.

## Risks

The deleted flag has different required behavior across leader transfer, split, and merge; the long in-code comment documents subtle ordering cases. Incorrectly filtering deleted-marked locks can either resurrect deleted locks or lose locks that must migrate. Memory accounting is manual and global; missed subtracts or double subtracts would skew the metric and potentially reject future locks incorrectly. `group_by_regions` uses `unwrap_or_else(|idx| idx - 1)`, which assumes all removed keys belong to some supplied region and regions cover the keyspace; invalid region inputs can underflow or misroute locks. `scan_locks` clones lock data and can be expensive for large limits. The packed timestamp status must be updated with compare/exchange discipline outside this file or stale sync tasks can incorrectly enable reads after leadership changes.

## Test Signals

Local tests cover per-peer and global memory accounting on insert/overwrite/remove/clear/drop, rejection when peer or global memory limits are exceeded, grouping locks by split regions including deleted-marked locks and rightmost/leftmost ranges, and `scan_locks` behavior for start/end bounds, filters, limits, and `has_more`. The tests serialize global gauge access with a mutex and reset it with `defer`, which is important because the gauge is process-global.
