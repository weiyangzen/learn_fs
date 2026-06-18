# sources/object-store/rustfs/crates/ecstore/src/rebalance.rs

## Purpose

`rebalance.rs` implements RustFS ECStore pool rebalancing: it decides which pools should give up object data to restore a cluster-wide free-space ratio, persists rebalance progress in object-store metadata, starts and stops asynchronous pool workers, lists source objects by disk set, migrates each object version into the normal data-movement path, and records progress, terminal status, deferred transient failures, and source-cleanup warnings.

The file is intentionally broad. It contains production workflow code plus a large unit-test module for metadata state transitions, migration classification, retry behavior, queue manipulation, and compatibility with older serialized metadata. The core external behavior is that a rebalance operation is represented by `rebalance.bin` in the RustFS metadata bucket, while in-memory `ECStore.rebalance_meta` carries the active cancellation token and current stats snapshot.

## Important APIs, Types, and Functions

`RebalanceStats` is the per-pool progress record. It stores initial free/capacity, pending and completed bucket queues, last bucket/object, object/version/byte counters, participation flag, `RebalanceInfo`, and `RebalanceCleanupWarnings`. `update` and `update_batch` increment object/version counts and estimate on-disk bytes using erasure data/parity block counts; deleted entries and invalid data block counts add zero bytes.

`RebalanceInfo` stores start/end timestamps, last error, and a `RebalStatus` enum (`None`, `Started`, `Completed`, `Stopped`, `Failed`). `RebalanceCleanupWarnings` tracks non-fatal source cleanup delete failures separately from terminal `last_error`. `RebalanceMeta` is the persisted operation state: operation id, percent-free target, stopped time, pool stats, and skipped runtime-only fields `cancel` and `last_refreshed_at`.

`MigrationBackend` abstracts source-pool operations for tests and production `SetDisks`: `get_object_reader_for_migration`, `delete_object_for_migration`, and `move_remote_version_for_migration`. `migrate_entry_version` and its injectable-wait variant implement version-level migration handling for normal object data, delete markers, and remote-tiered versions.

`ECStore::init_rebalance_meta` computes the global percent-free goal from `StorageAdminApi::storage_info`, initializes a `RebalanceStats` entry per pool, marks only pools below the goal as participating, persists a merged metadata snapshot, and installs it in memory. `load_rebalance_meta`, `update_rebalance_stats`, `save_rebalance_stats`, and `save_rebalance_meta_with_merge` are the metadata load/save path.

`ECStore::start_rebalance` validates that decommission is not running and metadata exists, attaches a cancellation token, completes any already-satisfied pools, resolves local participating pools from endpoint topology, and spawns `rebalance_buckets` workers for local pools only. `stop_rebalance` cancels the token, marks started pools stopped, and persists a stop snapshot.

`rebalance_buckets` is the per-pool driver. It runs a periodic save task, repeatedly selects the next bucket, calls `rebalance_bucket`, defers buckets with transient entry failures once by moving them to the back of the queue, marks successful buckets done, and sends a terminal signal to the save task so metadata reaches `Completed`, `Stopped`, or `Failed`.

`rebalance_bucket` loads lifecycle/object-lock/replication configs, lists objects from every disk set in the pool, and dispatches per-entry work under a semaphore sized to the number of disk sets. `SetDisks::list_objects_to_rebalance` uses online disks, a majority listing quorum, `list_path_raw`, and `MetaCacheEntries::resolve` to feed agreed or resolved partial entries into the callback.

`rebalance_entry` is the object-level workflow. It skips directories and completed pools, resolves `FileInfo` versions, sorts newer versions first while keeping missing mod-times later, applies lifecycle data-movement skip logic, skips a final delete marker when replication is not configured, migrates each remaining version, batches stats updates, and deletes the source prefix when all versions are considered safely rebalanced.

Retry and classification helpers include `is_transient_rebalance_error`, `should_retry_rebalance_listing`, `rebalance_listing_retry_delay`, `rebalance_migration_retry_delay`, `rebalance_lock_retry_delay`, and `wait_rebalance_listing_retry`. Lock/RPC timeout-like failures get jittered exponential-ish delay capped by `REBALANCE_MIGRATION_LOCK_RETRY_CAP`; generic transient migration/listing errors use linear 250 ms increments.

Metadata merge helpers (`merge_rebalance_meta`, `merge_rebalance_pool_stats`, `merge_rebalance_bucket_lists`, `remove_rebalanced_buckets_from_queue`, `merge_rebalance_cleanup_warnings`) protect concurrent local snapshots from overwriting terminal states or losing queue/progress information.

## Control Flow

The normal lifecycle starts with `init_rebalance_meta`, which snapshots disk capacity/free space and decides pool participation against the computed cluster free-space ratio. `start_rebalance` then attaches a cancellation token and spawns one worker per local participating pool. Each pool worker periodically saves stats while processing the bucket queue.

For each bucket, `rebalance_bucket` creates one listing job per disk set. Listing callbacks acquire an entry semaphore, then spawn `rebalance_entry` tasks. The job waits for both listing completion and all entry tasks. A first hard entry error cancels the callback token and is returned. A first transient deferred outcome is returned as a bucket deferral rather than an immediate terminal failure.

For each entry, `rebalance_entry` resolves versions and processes them serially. Remote-tiered versions are moved by `decommission_tiered_object`; delete markers are recreated through `delete_object`; normal versions are read from the source pool and passed to `data_movement::migrate_object` through `rebalance_object`. Missing objects or versions are treated as ignored and cleanup-safe. Non-transient failures stop the entry. Transient failures set a prefixed last-error and ask the bucket driver to retry the bucket later.

Pool completion can happen when the bytes moved plus initial free space reaches the percent-free goal, or when the bucket queue becomes empty. Deferred transient errors intentionally block goal-based completion until the bucket later succeeds and clears the prefixed last error.

Stop flow is cooperative. `stop_rebalance` cancels the in-memory token and records `stopped_at`; workers observe cancellation through `CancellationToken`, return `OperationCanceled`, and the save task classifies that terminal signal as `Stopped`. Helper logic prevents a later completion/failure signal from overwriting an already stopped state.

## State and Persistence Behavior

The persistent object is `rebalance.bin`, written through `save_config_with_opts` and read through `read_config_with_metadata`. The file format prepends two little-endian `u16` fields (`REBAL_META_FMT`, `REBAL_META_VER`) to an `rmp_serde` MessagePack encoding of `RebalanceMeta`.

`RebalanceMeta::load_with_opts` treats an empty payload as no-op metadata, rejects payloads shorter than the four-byte header, rejects unknown format/version values, deserializes the state, and sets `last_refreshed_at` to now. `RebalanceMeta::save_with_opts` skips saving when `pool_stats` is empty, then writes the header and serialized payload.

Saves are protected by a namespace write lock on the metadata bucket/object. `save_rebalance_meta_with_merge` reloads the remote metadata under `no_lock`, merges the local snapshot, and saves the merged result. This reduces lost updates when multiple local pool workers persist progress.

Runtime-only state is deliberately not persisted. `cancel` and `last_refreshed_at` are serde-skipped, so a restarted node must reload metadata and attach a fresh cancellation token before running workers. Bucket queues, completed buckets, stats, status, end times, last errors, and cleanup warning summaries are persisted.

State transitions are conservative: terminal `Failed` and `Stopped` states are protected from being overwritten by stale `Started` or `Completed` snapshots. A changed operation id replaces the remote metadata with the local operation. Cleanup warnings merge by count max and latest timestamp.

## Dependencies and Integration Points

The module integrates with `ECStore`, `SetDisks`, `StorageAPI`, `ObjectIO`, `NamespaceLocking`, and object operations from `store_api`. It uses `StorageAdminApi::storage_info` for capacity data and `get_global_endpoints` to decide whether a participating pool is local to this process.

Object enumeration depends on `cache_value::metacache_set::list_path_raw`, `MetaCacheEntry`, `MetaCacheEntries`, and `MetadataResolutionParams`. Migration depends on `data_movement::migrate_object`, `GetObjectReader`, `ObjectOptions`, `HTTPRangeSpec`, and `ObjectInfo`.

Bucket policy/config integration appears through lifecycle, object-lock retention, and replication config lookups. Lifecycle checks call `pools::should_skip_lifecycle_for_data_movement` with `LcEventSrc::Rebal`; replication state is preserved on delete marker moves.

Operational integration includes tracing events using the `ecstore`/`rebalance` component/subsystem constants, `CancellationToken` for worker cancellation, Tokio tasks/channels/semaphores for concurrency, and RustFS error classifiers for object-not-found, version-not-found, operation-canceled, and network/host-down conditions.

## Risks and Edge Cases

`rebalance.rs` is concurrency-heavy. Multiple spawned tasks update shared metadata snapshots while periodic save tasks merge with remote metadata. The merge helpers mitigate stale writes, but correctness depends on all updates flowing through the merge path and on status precedence rules staying aligned with operational expectations.

Source cleanup is intentionally best-effort. If deleting the old source prefix fails with anything except missing object/version, the rebalance still completes the entry and records only a warning. This avoids data-loss from failed cleanup blocking progress, but it can leave duplicate source data and may require operational visibility around `cleanup_warnings`.

Transient failure handling can defer a bucket only once per pool-worker run. A second deferred pass for the same bucket becomes terminal. This avoids infinite loops but risks failing long-lived partial outages that might recover after more delay.

The free-space accounting is an estimate based on erasure layout and file size, not a fresh capacity read for every migrated object. Incorrect `FileInfo` erasure metadata or skipped/lifecycle-expired versions can affect perceived goal progress. Tests cover invalid data blocks but real skew remains operationally significant.

`load_rebalance_bucket_configs` invokes versioning config only to map errors and discards the result. That may be intentional parity with other config loading, but the unused value is a maintenance signal.

Listing uses a majority quorum and resolves partial entries. If listing returns stale or inconsistent `MetaCacheEntry` versions, migration may see not-found and classify as cleanup-safe ignored. That behavior is probably necessary for concurrent deletes, but it can mask unexpected metadata races.

`REBAL_META_FMT` and `REBAL_META_VER` are both hard-coded as `1` with comments saying they replace actual values. Any future format change must preserve backward loading or version migration explicitly.

## Test Signals

The embedded `rebalance_unit_tests` module is extensive. It covers migration branches for remote versions, delete markers, normal reader/transfer paths, not-found cleanup-safe ignores, overwrite failures, transient retries, zero-attempt normalization, data-usage-cache skipping, and failure stage reporting.

State and metadata tests cover percent-free math, pool participation, goal completion, empty-queue completion, deferred-error blocking, start validation against decommission/missing metadata, terminal event classification, stopped-state preservation, cancellation token handling, save-option application, bucket queue operations, cleanup warning preservation, metadata merge precedence, legacy metadata deserialization without cleanup warning fields, and invalid metadata load error formatting.

Retry/classification tests cover SlowDown, erasure quorum failures, I/O timeouts, disk timeout wrapping, lock/RPC timeout messages, non-transient overwrite/access-denied/not-found cases, listing retry attempt limits, listing delay scaling, migration delay scaling, and cancellation-aware listing retry waits.

The tests are mostly unit-level and helper-level. They do not appear to run a full integration rebalance over real disks, `list_path_raw`, metadata bucket persistence, or actual `data_movement::migrate_object`; those remain important integration gaps for behavior under real erasure sets and concurrent object mutation.
