# sources/object-store/rustfs/crates/ecstore/src/store/rebalance.rs

## Purpose
This file contains pool-selection, cross-pool object lookup, rebalance/decommission deletion helpers, storage/admin introspection, namespace-lock factory routing, disk inventory lookup, and pool/set resolution for `ECStore`. Despite the filename, it is the central multi-pool placement and discovery layer used by object and multipart operations.

## Important APIs, Types, And Functions
- `LatestObjectInfoCandidate` and `resolve_latest_object_info_candidates` sort pool lookup results by object modification time, tie-breaking toward higher pool index.
- `RebalanceDeletePoolResult` and `resolve_rebalance_delete_from_all_pools_results` aggregate delete results across pools while preserving non-ignorable errors.
- `build_server_pools_available_space` computes per-pool available capacity and max-used percentage from disk info.
- `get_available_pool_idx` and `get_available_pool_idx_excluding` perform weighted random pool selection based on available capacity after reserve/fill filtering.
- `get_pool_idx`, `get_pool_idx_no_lock`, `get_pool_idx_existing_with_opts`, and `get_pool_info_existing_with_opts` locate the pool containing an existing object or choose capacity for a new object.
- `get_latest_object_info_with_idx` queries all pools and returns the latest object info without converting delete markers into access errors.
- `delete_object_from_all_pools` supports cleanup of objects that may exist in several pools or have read-quorum ambiguity.
- Admin/storage helpers include `reload_pool_meta`, `deduplicate_disks`, `handle_backend_info`, `handle_storage_info`, `handle_local_storage_info`, `handle_get_disks`, `handle_set_drive_counts`, and `handle_get_pool_and_set`.
- `handle_new_ns_lock` returns a namespace lock wrapper from the first pool.

## Control Flow
Capacity selection queries each pool concurrently, skipping suspended or actively rebalancing pools. It collects disk inventory for the object key, maps disks to `DiskInfo`, computes available capacity, filters pools over the reserve threshold, then picks a random point in total available capacity so larger free pools are more likely targets.

Existing-object lookup queries every pool concurrently. Unless `metadata_chg` is set, per-pool lookup clears `version_id` to find latest object state. Results are sorted by modification time. The scan skips decommissioned/rebalancing pools when requested, returns the first successful pool, treats `ErasureReadQuorum` as a usable pool indicator for non-metadata changes, honors delete-marker/precondition special cases, and otherwise returns not-found or the first non-not-found error.

Latest-object lookup is similar but simpler: query all pools, collect candidates, sort by mod time/high pool index, return the first object info, or propagate non-not-found errors, or synthesize object/version-not-found.

Delete-from-all-pools iterates supplied pool/error records, records write-quorum errors as hard failures, deletes from indexed pools, and requires aggregate success without hiding later non-ignorable errors.

Admin methods aggregate backend/storage info from pools or notification systems, defensively deduplicate disk entries, and resolve pool/set/disk index by disk UUID in stored erasure format metadata.

## State And Persistence Behavior
This file mostly reads state and delegates persistence:
- Pool metadata is read for suspension checks and can be reloaded into `self.pool_meta`.
- Rebalance state is consulted through `is_pool_rebalancing`.
- Object deletes persist through pool-level `delete_object`.
- Storage/admin info is read from notification systems and local pool snapshots.
- Capacity selection reads disk info but does not reserve space; actual allocation occurs later in pool PUT/complete paths, so placement is advisory and race-prone under concurrent writes.

## Dependencies And Integration Points
The module depends on global storage class configuration, storage admin traits, pool metadata, disk info helpers from `peer.rs`, object options and error classifiers, random selection, async `join_all`, madmin data types, namespace locks, erasure format metadata, and `PoolAvailableSpace`/`ServerPoolsAvailableSpace` filtering helpers. It is heavily consumed by `object.rs`, `multipart.rs`, and admin APIs.

## Risks And Edge Cases
- Weighted random placement is based on a point-in-time disk info snapshot; concurrent writes can still race into full pools.
- Existing-object lookup clears `version_id` unless `metadata_chg` is set; callers needing exact version lookup must set the right option, and helper functions in `object.rs` do this explicitly.
- Tie-breaking latest objects by higher pool index on identical modification times is deterministic but encodes a policy that may matter during rebalance/expansion.
- `is_suspended` has a TODO for locking; it currently reads `pool_meta` under an async `RwLock`, but broader consistency with updates may need review.
- `delete_object_from_all_pools` is sequential over supplied pools, not concurrent; large multi-pool cleanup could be slower.
- Defensive disk deduplication hides upstream duplicate reporting but may also mask topology/reporting bugs unless warnings are monitored.

## Test Signals
This file contains unit tests for latest-object candidate ordering, delete-marker latest selection, non-not-found error propagation, version-aware not-found synthesis, pool lookup not-found errors, rebalance pool-meta error wrapping, aggregate rebalance delete behavior across success/not-found/write-quorum/non-ignorable failures, disk set lookup error formatting, and available-space computation including meta-bucket capacity guard bypass. Additional integration tests are needed for live pool selection, suspension/rebalance skips, storage info deduplication with notification systems, and namespace-lock routing.
