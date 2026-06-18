# sources/object-store/rustfs/crates/notify/src/global.rs

## Purpose
Provides the process-global notification system and the main notification entry points used by object operations and bucket notification management.

## Important APIs, types, and functions
- Static `NOTIFICATION_SYSTEM: OnceLock<Arc<NotificationSystem>>`.
- `initialize` creates a `NotificationSystem`, runs async initialization, then stores it once.
- `initialize_live_events` stores a system without loading configured targets/rules so live listeners can receive in-process events.
- `notification_system`, `is_notification_system_initialized`, `notification_metrics_snapshot`, and `notification_target_metrics` expose global state.
- `notifier_global::notify` builds and sends an `Event` unless the system is uninitialized or the operation is a RustFS replication request.
- `add_bucket_notification_rule`, `add_event_specific_rules`, and `clear_bucket_notification_rules` are public helpers around bucket rule loading/clearing.

## Control flow
`initialize` constructs and initializes the full runtime before setting `OnceLock`, so failure to build targets prevents global publication. `notifier_global::notify` fetches the global system, logs and returns if absent, filters replication events, constructs `Event::new(args)`, and sends through `NotificationSystem::send_event`. Rule helpers build `BucketNotificationConfig` with patterns from prefix/suffix inputs, then call into `NotificationSystem`.

## State and persistence behavior
The global `OnceLock` can only be set once per process. Bucket rule helper calls update in-memory bucket rule state through the notification system; target config persistence is handled elsewhere by `NotifyConfigManager`. Metrics snapshots return defaults when the global system does not exist.

## Dependencies and integration points
Connects object-store operations to `NotificationSystem`, `EventArgs`, `EventName`, `BucketNotificationConfig`, `TargetID`, and `rustfs_config::server_config::Config`. This is the major public integration surface re-exported by `lib.rs`.

## Risks and edge cases
There is no reset path for tests or process reconfiguration after `OnceLock` is set. `initialize_live_events` intentionally bypasses configured targets/rules, so external notifications remain disabled in that mode. The `add_event_specific_rules` helper calls `new_pattern(Some(prefix), Some(suffix))` even when either string is empty, which still works for many cases but differs from the explicit empty filtering used by `add_bucket_notification_rule`.

## Test signals
No direct test module in this file. Its behavior is indirectly exercised by notification system integration tests, event replication filtering tests, and bucket config/rule engine tests.
