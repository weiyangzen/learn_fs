# sources/object-store/rustfs/crates/ecstore/src/store/object.rs

## Purpose
This file implements the core `ECStore` object operations: GET reader/info, PUT, COPY, DELETE, batch delete, tags, metadata, transition/restore, data movement/decommission handling, and object-integrity verification. It also wraps namespace-lock acquisition with diagnostics and adapts multi-pool object placement to versioning, delete markers, rebalance, decommission, and tiered-object workflows.

## Important APIs, Types, And Functions
- `LockGuardedReader` keeps a read namespace lock alive while a `GetObjectReader` stream is consumed and releases it after EOF when lock optimization is disabled.
- `ObjectLockDiagMode` and `ObjectLockDiagGuard` record lock hold/acquire metrics and warn when thresholds are exceeded.
- `acquire_object_write_lock_if_needed` / `acquire_object_read_lock_if_needed` create namespace locks through `handle_new_ns_lock`, map quorum failures to `StorageError::NamespaceLockQuorumUnavailable`, set `opts.no_lock = true`, and return diagnostic guards.
- `select_data_movement_pool_idx`, `find_data_movement_target_info`, `has_equivalent_data_movement_delete_marker`, and `has_equivalent_data_movement_tiered_object` protect decommission/data-movement resume semantics.
- `decommission_tiered_object` relocates metadata for already transitioned objects during pool decommission.
- `handle_get_object_reader`, `handle_get_object_info`, `handle_put_object`, `handle_copy_object`, `handle_delete_object`, and `handle_delete_objects` are the primary object API handlers.
- Metadata/tag/transition helpers include `handle_add_partial`, `handle_transition_object`, `handle_restore_transitioned_object`, `handle_put_object_metadata`, `handle_get_object_tags`, `handle_put_object_tags`, `handle_delete_object_version`, `handle_delete_object_tags`, and `handle_verify_object_integrity`.

## Control Flow
Object names are normalized through `encode_dir_object` before pool calls and decoded for returned user-visible names where needed. Single-pool deployments usually delegate directly to `self.pools[0]`. Multi-pool deployments first locate the latest accessible object or choose a target pool:
- GET reader/info acquires a read lock unless `opts.no_lock`, finds the latest object across pools, rejects delete markers with S3-like not-found/method-not-allowed semantics, applies preconditions for info, and delegates to the selected pool.
- PUT validates arguments, encodes directory objects, selects a target by existing object/data-movement logic or capacity, rejects data movement writes that would land back in the source pool, then delegates to the chosen pool.
- COPY handles same-source/destination specially. Same object/version metadata copies stay in the existing pool. Non-versioned self-copy of transitioned objects may restore by writing from `put_object_reader`. Other copies choose a destination pool and write through `put_object`.
- DELETE handles prefix deletes separately, acquires a write lock for exact deletes, performs data-movement-specific target selection/resume checks when requested, otherwise locates the pool containing the object. For non-versioned deletes with multiple candidate pools/read-quorum signals it can call `delete_object_from_all_pools`; otherwise it scans pools and ignores not-found/version-not-found until a delete succeeds.
- Batch delete currently broadcasts the full encoded object list to every pool, then for each object picks the first successful found deletion or the first recorded error/result.
- Transition, restore, tags, and metadata update operations find the latest accessible pool and delegate.

## State And Persistence Behavior
Persistent object data and metadata are written by the pool/set layers, but this file determines placement, locking, and cross-pool mutation semantics:
- Writes and deletes mutate the selected erasure pool.
- Batch deletes mutate all pools and reconcile per-object results after the fact.
- Data movement paths avoid overwriting source-pool versions and allow idempotent resume when an equivalent target delete marker or transitioned object already exists.
- `opts.metadata_chg` is set for version-aware lookups and metadata updates so lower layers preserve version IDs instead of coercing to latest lookups.
- Read locks can be held until stream EOF to preserve atomic-read semantics unless lock optimization is enabled.
- `verify_object_integrity` drains a GET reader stream to `tokio::io::sink`, exercising the read path without storing the object in memory.

## Dependencies And Integration Points
The file integrates with namespace locking (`rustfs_lock`), object lock diagnostics metrics (`rustfs_io_metrics`), storage class/data movement pool selection from `rebalance.rs`, object and file metadata types from `rustfs_filemeta`, lifecycle/tiering transition types, HTTP headers and range specs, object option precondition checks, erasure pool methods, error classifiers, directory-object encoding/decoding, and async I/O traits. It is one of the main consumers of `get_latest_object_info_with_idx`, `get_pool_info_existing_with_opts`, `get_pool_idx`, and `delete_object_from_all_pools`.

## Risks And Edge Cases
- Batch delete has a TODO for namespace locks and currently broadcasts all deletes to all pools, which may be expensive and has more mutation surface than targeted deletes.
- `handle_delete_object_version` is not implemented for multi-pool deployments.
- `handle_copy_object` relies on `src_info.put_object_reader` for data-copy paths and returns `InvalidArgument` if absent; callers must prepare the reader.
- Lock guard lifetime differs based on `ENV_OBJECT_LOCK_OPTIMIZATION_ENABLE`; readers must be drained or dropped promptly to avoid long lock holds.
- Delete marker semantics are intentionally split: low-level latest lookup can return delete markers, while higher-level access converts them to errors. New callers must use the correct helper.
- Data movement resume equivalence checks compare version, mod time, etag/checksum/transition fields; missing or inconsistent metadata can cause safe but disruptive overwrite errors.
- Several TODO/commented paths indicate incomplete lock optimization/batch-delete redesign.

## Test Signals
The file has extensive unit tests around data movement target selection, delete-marker equivalence and resume, tiered-object equivalence and resume, latest-object delete-marker access semantics, contextual decommission error wrapping, version-aware lookup option construction, data movement skip flags, and lock-guard behavior with optimization disabled. The lock tests verify that read locks block writers until reader drop or EOF. Integration coverage is still needed for full multi-pool object placement, copy, batch delete, and transition/restore flows.
