# sources/object-store/rustfs/crates/notify/src/notification_system_subscriber.rs

## Purpose
Maintains a fast, consistent subscriber view per bucket for pre-dispatch checks such as `has_subscriber`.

## Important APIs, types, and functions
- `NotificationSystemSubscriberView` wraps a `SubscriberIndex`.
- `new` creates an empty index.
- `has_subscriber(bucket, event)` checks the index using the event mask in the current snapshot.
- `apply_bucket_config` compiles a `BucketNotificationConfig` into a `BucketRulesSnapshot`, debug-checks mask consistency, and atomically stores it.
- `clear_bucket` clears a bucket's snapshot.

## Control flow
Bucket config loading calls `apply_bucket_config` after rule compilation. Read paths call `has_subscriber`, which is a quick snapshot/mask read without reconstructing rules.

## State and persistence behavior
State is in-memory only, stored inside `SubscriberIndex` using `ArcSwap` snapshot cells. Persistence of bucket notification XML/config is outside this file.

## Dependencies and integration points
Depends on `BucketNotificationConfig`, `SubscriberIndex`, `BucketRulesSnapshot`, `DynRulesContainer`, and `EventName`. It is created in `NotificationSystem::new` and passed into `NotifyBucketConfigManager`.

## Risks and edge cases
Correctness depends on compiling masks and rules from the same source. The debug assertion catches inconsistent mask computation in debug builds only. This view is a subscriber fast path, not the authoritative dispatch matcher; it must stay in sync with `NotifyRuleEngine`.

## Test signals
No local tests. Indirect tests in services, rule config, and bucket config manager paths validate empty setup and compiled subscriber behavior.
