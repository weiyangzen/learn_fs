# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/bucket_lifecycle_ops.rs

## Purpose

This file is the operational side of bucket lifecycle management in RustFS ecstore. It turns lifecycle evaluation results into side effects: queuing and executing expiry work, queuing and executing tier transitions, expiring transitioned objects from remote warm tiers, deleting local object versions, scheduling replication delete work, validating transition tiers, restoring transitioned objects, and periodically cleaning stale multipart upload state.

It sits between lifecycle policy evaluation (`core.rs` and `evaluator.rs`), bucket metadata systems, object APIs on `ECStore`, remote tier drivers, replication, object lock, event notification, and scanner metrics. The file owns long-lived global worker state through `GLOBAL_ExpiryState` and `GLOBAL_TransitionState`.

## Important APIs, Types, and Functions

- `LifecycleSys` wraps lifecycle config lookup through `metadata_sys::get_lifecycle_config` and exposes `trace` closures for lifecycle audit/debug logging.
- `ExpiryOp`, `ExpiryTask`, `FreeVersionTask`, `NewerNoncurrentTask`, and `Jentry` form the dynamic task set consumed by expiry workers.
- `ExpiryState` owns per-worker Tokio MPSC channels, missed-task counters, worker resizing, and the expiry worker loop.
- `TransitionTask`, `TransitionWorker`, `TransitionState`, and `ImmediateEnqueueFailure` own transition queueing, async-channel backpressure handling, worker resizing, active task metrics, compensation backfill, and last-day tier stats.
- `init_background_expiry`, `TransitionState::init`, and `init_background_stale_multipart_upload_cleanup` start the background systems.
- `validate_transition_tier` checks lifecycle transition storage classes against `GLOBAL_TierConfigMgr`.
- `enqueue_transition_immediate`, `enqueue_immediate_expiry`, `enqueue_transition_for_existing_objects`, and `enqueue_expiry_for_existing_objects` are scanner/S3 event entry points that evaluate lifecycle rules and enqueue or apply work.
- `transition_object`, `get_transitioned_object_reader`, `expire_transitioned_object`, `apply_expiry_on_transitioned_object`, and `apply_expiry_on_non_transitioned_objects` are the main object-operation side effects.
- `post_restore_opts`, `put_restore_opts`, and `RestoreRequestOps::validate` build and validate restore-related `ObjectOptions`.
- `LifecycleOps for ObjectInfo` converts storage object metadata into lifecycle `ObjectOpts` and identifies remote transitioned objects.
- `eval_action_from_lifecycle` is a secondary guard around `lc.eval`, suppressing deletes that conflict with object lock or active replication.
- `apply_lifecycle_action`, `apply_expiry_rule`, and `apply_transition_rule` are dispatch helpers used by scanner-like callers.
- Multipart cleanup helpers (`read_stale_multipart_candidate`, `stale_upload_lifecycle_due`, `cleanup_stale_multipart_uploads_in_set`, etc.) discover incomplete multipart metadata on disks, evaluate abort rules, and delete stale upload directories.

## Control Flow

Expiry work starts when callers call `apply_expiry_rule`, `enqueue_immediate_expiry`, or scanner enqueue paths. `ExpiryState::enqueue_by_days` hashes a task by bucket/object and routes it to a stable worker channel. `ExpiryState::worker` receives boxed `ExpiryOp` values, downcasts to the concrete task type, and dispatches:

- `ExpiryTask` calls `apply_expiry_on_transitioned_object` if the object is already transitioned, otherwise `apply_expiry_on_non_transitioned_objects`.
- `NewerNoncurrentTask` batches noncurrent-version deletes through `delete_object_versions`.
- `Jentry` deletes an object from a remote tier journal entry.
- `FreeVersionTask` deletes remote tier state and then deletes the local free-version marker from a pool set.

Transition work starts when lifecycle evaluation returns `TransitionAction` or `TransitionVersionAction`. `TransitionState::queue_transition_task` uses a bounded async-channel. Immediate S3 write sources first try `try_send`, then wait for `transition_queue_send_timeout`; on timeout or closed queues they schedule per-bucket compensation through `enqueue_transition_for_existing_objects`. Scanner sources do not block; queue-full scanner attempts are recorded and deferred to future scans/backfill. `TransitionState::worker_with_cancel` receives tasks, calls `transition_object`, records metrics, updates daily tier stats, and sends object transition complete/failed events.

Existing-object scanning flows page through `list_object_versions` with marker/version-marker continuation. Transition scanning calls `enqueue_transition_with_lifecycle` for every version. Expiry scanning calls `eval_action_from_lifecycle`, delays once for recent date-expiry config changes, and either applies due deletes immediately or enqueues them.

Stale multipart cleanup periodically lists local multipart sha directories on each set, reads `xl.meta` metadata when available, merges duplicate disk candidates by preferring metadata-rich records, computes the earlier of default stale expiry and lifecycle `AbortIncompleteMultipartUpload` due time, deletes due upload directories through `set.delete_all`, and then removes empty multipart sha directories from local disks.

## State and Persistence Behavior

Global in-memory state:

- `GLOBAL_ExpiryState` stores expiry worker channels, receiver handles, and counters for missed expiry, free-version, tier journal tasks, and worker count.
- `GLOBAL_TransitionState` stores the bounded transition queue, worker cancellation tokens/handles, active task counters, queue-full/timeout counters, compensation-bucket deduplication, and last-day tier stats.

Persistent side effects:

- Local object and version metadata are mutated via `ECStore::delete_object`, set-level `delete_object_version`, and `api.transition_object`.
- Remote tier objects are deleted via `delete_object_from_remote_tier`; transitioned reads use tier drivers from `GLOBAL_TierConfigMgr`.
- Multipart metadata under `RUSTFS_META_MULTIPART_BUCKET` is read and deleted directly through disk/set APIs.
- Lifecycle configs, object-lock configs, and replication configs are read from bucket metadata systems.
- Delete replication work is scheduled by constructing `DeletedObjectReplicationInfo` and calling `schedule_replication_delete`.
- S3 event notifications are emitted for lifecycle expiration and transition complete/failure.

Notable persistence safeguards include setting `ObjectOptions.expiration.expire`, choosing `version_id` for version deletes, setting `delete_prefix`/`delete_prefix_object` for delete-all lifecycle actions, marking `skip_decommissioned` only after remote-tier delete success, and preserving user metadata/tags when building restore options.

## Dependencies and Integration Points

The file depends on:

- lifecycle policy types/functions from `core.rs` and version-aware `Evaluator` from `evaluator.rs`.
- lifecycle audit source/action data from `bucket_lifecycle_audit`.
- tier journal and warm backend APIs from `tier_sweeper`, `tier_last_day_stats`, and `tier::warm_backend`.
- bucket metadata, versioning, object lock, replication, event notification, metrics, and global service cancellation.
- `ECStore` plus object/list/multipart operation traits from `store_api`.
- `s3s::dto` lifecycle, restore, replication, and timestamp DTOs.
- `rustfs_filemeta` metadata helpers for restore status, replication state, and free-version markers.

This file is a central integration point for scanner-driven ILM behavior and immediate S3 write-path ILM behavior. It also provides reader support for transitioned objects, so GET paths can retrieve data from configured warm tiers.

## Risks and Edge Cases

- Worker queues are bounded and can drop/defer work. The code tracks missed tasks and schedules transition compensation for immediate-source transition failures, but expiry enqueue failures depend on future scans.
- `ExpiryState` uses a write lock around enqueue calls; long or repeated enqueues can contend with worker resizing.
- Several operations deliberately treat object-not-found/version-not-found as benign, but remote tier failures may leave remote data or local metadata divergent until journal/compensation catches up.
- Transition worker counters must stay balanced around all success and error paths; task panic would leave active counts wrong.
- Date-expiry config update grace is a single 5-second delay for an existing-object scan; highly concurrent config updates may still race scanner decisions.
- `LifecycleOps::to_lifecycle_opts` omits some `ObjectInfo` fields (`user_defined`, replication status) that `core.rs` can evaluate, while `enqueue_immediate_expiry` constructs options through the same helper before `Evaluator`; callers that need lock/replication metadata must pass it separately.
- Stale multipart cleanup reads local disks and deletes set paths; incorrect metadata parsing or upload-id encoding would risk deleting active uploads, although initiation time and lifecycle/default due checks reduce this.
- `Transition::next_due` in `core.rs` unwraps `obj.mod_time`; transition callers must provide valid `mod_time`.

## Test Signals

This file has extensive unit and integration-style tests under its `tests` module. Coverage includes expiry enqueue misses without workers, scanner transition queue full metrics, queue capacity and timeout environment handling, transition worker resizing/cancellation, compensation deduplication, date-expiry grace checks, remote delete option handling, lifecycle deleted-object construction, replication state construction/reuse, stale multipart candidate merge behavior, stale multipart cleanup with default expiry and lifecycle abort rules including size filters, multipart metadata sanitization, repeated part overwrite behavior, and empty multipart sha-directory cleanup. One ECStore fresh-boot test is ignored because it requires isolated global object layer state.
