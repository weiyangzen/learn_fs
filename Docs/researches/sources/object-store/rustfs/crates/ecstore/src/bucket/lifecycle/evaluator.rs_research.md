# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/evaluator.rs

## Purpose

This file provides a version-list evaluator around the core lifecycle policy. It evaluates all versions of one object together so lifecycle delete-all behavior, noncurrent-version counting, object-lock suppression, and replication suppression can be applied consistently across a version stack.

## Important APIs, Types, and Functions

- `Evaluator` stores an `Arc<BucketLifecycleConfiguration>` plus optional object-lock retention config and optional replication config.
- `Evaluator::new` constructs the evaluator for a lifecycle policy.
- `with_lock_retention` and `with_replication_config` attach optional guard configs.
- `is_pending_replication` checks for active replication rules and non-empty version purge status.
- `is_object_locked` checks bucket object-lock enablement and then delegates metadata-level retention checks to `is_object_locked_by_metadata`.
- private `eval_inner` evaluates an ordered `&[ObjectOpts]` at a supplied time and returns parallel `Event` values.
- public `eval` validates that the input slice is non-empty and that `objs.len() == objs[0].num_versions`, then evaluates using current UTC time.

## Control Flow

`eval` first enforces version-count consistency. `eval_inner` initializes default events, tracks `newer_noncurrent_versions`, and walks versions in order. For each object version it asks `policy.eval_inner(obj, now, newer_noncurrent_versions)` for a raw lifecycle event.

Delete-all actions are special. If object lock is enabled for the bucket, they are suppressed. Otherwise the event is recorded for that version and the evaluator stops scanning the remaining versions, because deleting all versions makes later per-version decisions unnecessary.

Version delete actions are sanitized defensively. A version delete for a nil/missing version id becomes `NoneAction`; object-lock metadata suppresses deletion; pending replication suppresses deletion. After event handling, the evaluator increments `newer_noncurrent_versions` for non-latest versions that are not being deleted, preserving newer noncurrent versions for later rule decisions.

## State and Persistence Behavior

The evaluator has no persistence and no background state. It reads policy/config objects passed by `Arc`, inspects `ObjectOpts`, and returns a vector of lifecycle `Event` values. Actual deletes, transitions, and replication scheduling happen in `bucket_lifecycle_ops.rs`.

## Dependencies and Integration Points

The evaluator depends on:

- `core.rs` through `Lifecycle`, `Event`, and `ObjectOpts`.
- `objectlock_sys::is_object_locked_by_metadata` for retention checks.
- `ReplicationConfig` plus `ReplicationConfigurationExt::has_active_rules`.
- `s3s::dto` object-lock and lifecycle DTOs.
- `IlmAction` for action matching.

It is used by `enqueue_immediate_expiry` in `bucket_lifecycle_ops.rs`, which builds a full version list for a just-written object name, attaches object-lock and replication configs from bucket metadata, evaluates events, and then applies or batches due expiry actions.

## Risks and Edge Cases

- Correct behavior depends on the caller passing all versions for a single object in the order expected by `newer_noncurrent_versions` accounting.
- `eval` only compares the slice length to `objs[0].num_versions`; it does not verify that every `ObjectOpts` belongs to the same object name or bucket.
- `is_pending_replication` checks `!obj.version_purge_status.is_empty()` under active rules, so replication suppression is tied to how `ObjectOpts` was populated. If callers omit purge status, deletes may not be suppressed here.
- Delete-all actions stop scanning remaining versions only when object lock does not suppress them; this is intentional but makes object-lock configuration a major branch in version-stack behavior.

## Test Signals

There are no local tests in this file. Behavior is indirectly covered by lifecycle operation tests that call immediate expiry evaluation and by core lifecycle tests that cover raw event calculation. Direct tests would be valuable for version order, `num_versions` mismatch errors, object-lock suppression, pending replication suppression, and delete-all short-circuit behavior.
