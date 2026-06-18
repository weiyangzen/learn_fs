# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/core.rs

## Purpose

This file is the policy-evaluation core for bucket lifecycle rules. It validates S3 lifecycle configurations, matches lifecycle rules against object metadata, computes due times for expiration and transition actions, chooses the highest-priority lifecycle event for an object/version, and defines the object/event option structures consumed by operational code in `bucket_lifecycle_ops.rs`.

It implements lifecycle behavior directly on `s3s::dto::BucketLifecycleConfiguration` and related DTOs, while re-exporting `IlmAction` as the action enum used across the lifecycle package.

## Important APIs, Types, and Functions

- Constants `TRANSITION_COMPLETE` and `TRANSITION_PENDING` define transition status markers shared with object metadata.
- `RuleValidate for LifecycleRule` validates rule-level constraints: legacy prefix/filter conflict, delete-marker-with-tags conflict, and at least one lifecycle action.
- `lifecycle_rule_prefix` selects the effective non-empty prefix from legacy `Prefix`, `Filter.Prefix`, or `Filter.And.Prefix`.
- `Lifecycle for BucketLifecycleConfiguration` provides `has_transition`, `has_expiry`, `has_active_rules`, `validate`, `filter_rules`, `eval`, `predict_expiration`, `eval_inner`, and `noncurrent_versions_expiration_limit`.
- `LifecycleCalculate` provides `next_due` for `LifecycleExpiration`, `NoncurrentVersionTransition`, and `Transition`.
- `expected_expiry_time` implements S3-compatible day-based rounding to the configured ILM processing boundary, with `days == 0` returning `UNIX_EPOCH` for immediate expiry.
- `abort_incomplete_multipart_upload_due` computes the earliest due time for abort-incomplete-multipart-upload lifecycle rules.
- `ObjectOpts` is the normalized object/version input used by lifecycle evaluation.
- `Event` is the evaluation result, carrying `IlmAction`, rule id, due time, noncurrent limits, and storage class.
- `ExpirationOptions` and `TransitionOptions` are options attached to object operations when applying lifecycle actions.

## Control Flow

Validation starts at `BucketLifecycleConfiguration::validate`. It rejects more than 1000 rules, empty rule sets, invalid statuses, negative expiration/noncurrent days, non-midnight expiration dates, rule IDs over 255 characters, duplicate IDs, and object-lock-incompatible all-version/delete-marker actions. It delegates rule structural checks to `RuleValidate`.

Rule matching starts in `filter_rules`: disabled rules are skipped, effective prefixes must match the object name, tag filters are evaluated through `rule.rs`, and size bounds are applied for non-delete-marker objects. Matching rules are cloned and returned in lifecycle order.

Evaluation starts with `eval`, which passes `OffsetDateTime::now_utc()` into `eval_inner`. `eval_inner` rejects missing or zero modification times, adds restore-expiry delete events when restored copies have expired, then walks matching rules and pushes candidate events for:

- expired-object-delete-marker and `DelMarkerExpiration` delete-marker behavior,
- noncurrent version expiration by `NoncurrentDays`,
- noncurrent version transitions,
- latest or unversioned object expiration by date/days, including `ExpiredObjectAllVersions`,
- current-version transitions by date/days.

At the end, candidate events are sorted so already-due deletes win over transitions at the same due time, otherwise the earliest due event wins. If no event applies, a default `NoneAction` event is returned.

`predict_expiration` is a read-only prediction path for latest non-delete-marker objects. It ignores expired-object-delete-marker rules and returns the closest future or configured expiration event without requiring it to be due now.

`noncurrent_versions_expiration_limit` extracts the configured noncurrent retention counts/days for scanner batching logic.

## State and Persistence Behavior

This file has no durable persistence and no background state. It is pure policy logic apart from:

- current-time reads through `OffsetDateTime::now_utc`,
- environment reads for `RUSTFS_ILM_PROCESS_TIME` and deprecated `_RUSTFS_ILM_PROCESS_TIME`,
- debug logging for evaluation and expiry-time computation.

The output `Event` and option structs are later persisted indirectly by `bucket_lifecycle_ops.rs` when it deletes objects, transitions objects, or writes restore metadata.

## Dependencies and Integration Points

The file depends on `s3s::dto` lifecycle DTOs, `time`, `uuid`, `rustfs_config`, `rustfs_filemeta`, `rustfs_common::metrics::IlmAction`, and `crate::store_api::ObjectInfo`. Tag and size matching are delegated to `crate::bucket::lifecycle::rule::Filter`.

It is used by:

- `bucket_lifecycle_ops.rs` for scanner and immediate action decisions.
- `evaluator.rs` for version-list evaluation with object-lock and replication suppression.
- stale multipart cleanup for `AbortIncompleteMultipartUpload` due-time calculation.
- bucket lifecycle validation paths elsewhere in the metadata/API layer.

## Risks and Edge Cases

- `Transition::next_due` unwraps `obj.mod_time` when `days` is set; callers must ensure current-version transition candidates have a modification time.
- `has_active_rules` indexes the first transition with `rule_transitions[0]` when transitions are present, assuming non-empty vectors.
- `filter_rules` clones matching rules, which is simple but potentially expensive for very large rule sets near the 1000-rule limit.
- Some lifecycle logic only inspects the first transition/noncurrent transition, so multiple transition entries may not be fully honored.
- `eval_inner` accepts `_newer_noncurrent_versions` but currently does not use that argument; version-list logic in `evaluator.rs` tracks spared noncurrent versions separately, while this core method skips rules with `newer_noncurrent_versions > 0`.
- `Event::default` uses `due = UNIX_EPOCH`, so callers must check `action` and not treat default due as an actionable immediate event.
- Object-lock validation permits ordinary days-based expiration on locked buckets, but operational code must still check actual retention before deleting individual object versions.

## Test Signals

The test module is broad. It verifies zero and negative expiration days, zero and negative noncurrent days, abort-incomplete-only rules, non-midnight expiration dates, prediction selecting the closest expiry, duplicate and too-long rule IDs, case-sensitive status validation, latest object expiration before/after due, current and noncurrent transitions, noncurrent expiration including zero-day immediate expiry, noncurrent expiration-limit extraction, prefix/filter/tag matching, expired-object-delete-marker due behavior, object-lock compatibility for delete marker and all-version extensions, configurable processing-boundary rounding, legacy prefix/filter conflict rules, and `ExpiredObjectAllVersions` evaluation.
