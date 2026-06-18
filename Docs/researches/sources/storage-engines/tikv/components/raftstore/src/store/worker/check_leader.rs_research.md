# sources/storage-engines/tikv/components/raftstore/src/store/worker/check_leader.rs

## Purpose
This worker validates remote leader information against local region read progress and provides store-level safe-ts queries. It is part of TiKV stale-read/local-read coordination: followers consume leader-published read states, callers learn which regions still match their expected leader, and store-wide or key-range safe-ts can be computed.

## Important APIs, Types, and Functions
- `Task::CheckLeader { leaders, cb }` accepts `LeaderInfo` records and returns matching region IDs through a callback.
- `Task::GetStoreTs { key_range, cb }` returns the minimum non-zero safe-ts for all regions or for regions overlapping a key range.
- `Runner<S, E>` owns `store_meta`, a cloned `RegionReadProgressRegistry`, and a `CoprocessorHost<E>`.
- `Runner::new` extracts the registry from `StoreRegionMeta`.
- `get_range_safe_ts` implements the store-wide fast path and range-overlap path.

## Control Flow
For `CheckLeader`, the runner hits failpoints for stores 2 and 3, then delegates to `RegionReadProgressRegistry::handle_check_leaders`. That method consumes each incoming `LeaderInfo`, updates safe-ts/read-state if present, calls coprocessor hooks, and returns IDs whose leader term, peer ID, and epoch match local state. The task callback receives those IDs.

For `GetStoreTs`, an empty `KeyRange` scans the registry directly under its internal mutex and returns the minimum non-zero safe-ts, or zero if none are initialized. A non-empty range locks `store_meta`, searches overlapping regions with `StoreRegionMeta::search_region`, reads their registered safe-ts values, and returns the minimum non-zero value or zero.

## State and Persistence Behavior
The worker mutates in-memory `RegionReadProgress` via leader-info consumption. It does not write raft state or engine data. Safe-ts value zero is treated as uninitialized and excluded from minimum calculations. The range path depends on the current in-memory region range map and assumes every searched region has a registered read progress entry.

## Dependencies and Integration Points
The worker depends on `StoreRegionMeta`, `RegionReadProgressRegistry`, `CoprocessorHost`, `KvEngine`, `KeyRange`, `LeaderInfo`, and `tikv_util::worker::Runnable`. It integrates with stale-read/check-leader RPC handling and store metadata search over region key ranges.

## Risks and Edge Cases
The non-empty range branch calls `registry.get(&r.get_id()).unwrap()` for searched regions, so registry/meta consistency is required. Holding `store_meta` while scanning ranges can be more expensive than the empty-range fast path, which the comments say is the current common case. Zero safe-ts values are ignored, which avoids uninitialized peers but can hide a fully uninitialized range by returning zero.

## Test Signals
`test_get_range_min_safe_ts` builds synthetic regions and read-progress records, then verifies empty-store behavior, global minimum selection, zero safe-ts filtering, overlapping range minima, unbounded end ranges, and gaps returning zero.
