# sources/object-store/rustfs/crates/notify/src/rules/subscriber_snapshot.rs

## Purpose
Defines generic snapshot traits and the immutable bucket subscriber snapshot used by `SubscriberIndex`.

## Important APIs, types, and functions
- `RuleEvents` exposes subscribed event names.
- `RulesContainer` exposes an iterator over rules and a default `is_empty`.
- `BucketRulesSnapshot<R>` stores `event_mask` and `Arc<R>`.
- Methods: `empty`, `has_event`, `is_empty`, and `debug_assert_mask_consistent`.
- Type aliases: `DynRulesContainer` and `BucketSnapshotRef`.

## Control flow
Snapshot consumers check `event_mask` for fast event filtering. Debug builds can recompute the mask from rule event lists and assert consistency.

## State and persistence behavior
Snapshots are immutable in-memory values shared through `Arc`; replacement is handled by `SubscriberIndex`.

## Dependencies and integration points
Uses `EventName` and `Arc`. Implemented by the compiled rules adapter in `rules/config.rs` and used by subscriber view/index.

## Risks and edge cases
`is_empty` returns true if the mask is zero or the rules container is empty. If mask and rules diverge in release builds, the debug assertion would not run and subscriber checks may be wrong.

## Test signals
No direct tests. `NotificationSystemSubscriberView::apply_bucket_config` calls `debug_assert_mask_consistent`, and higher-level tests exercise subscriber behavior.
