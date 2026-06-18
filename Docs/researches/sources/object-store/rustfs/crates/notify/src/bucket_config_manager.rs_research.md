# sources/object-store/rustfs/crates/notify/src/bucket_config_manager.rs

Purpose: coordinates bucket-level notification configuration across target availability, subscriber snapshots, and rule-engine state.

Important APIs/types/functions: `NotifyBucketConfigManager` owns `Arc<EventNotifier>`, `NotifyRuleEngine`, and `Arc<NotificationSystemSubscriberView>`. `new` constructs it. `has_subscriber(bucket, event)` checks the fast subscriber view first, then confirms the rule engine. `load_bucket_notification_config(bucket, cfg)` validates targets and loads rules. `remove_bucket_notification_config(bucket)` clears subscriber and rule-engine state.

Control flow: load obtains available ARNs for the config region from the notifier. If none exist, it returns `NotificationError::Configuration(notify_configuration_hint())`. It logs validation details, calls `cfg.validate`, rejects most parse/config errors as `BucketNotification`, but treats `ParseConfigError::ArnNotFound` as a warning so configs referencing temporarily missing targets can still load. It then applies the config to the subscriber view and sets the bucket rules in the async rule engine.

State and persistence: no disk persistence. It mutates in-memory subscriber snapshot and sharded/async rule-engine state. Logging emits structured notify bucket-config events.

Dependencies/integration: depends on `BucketNotificationConfig`, `EventNotifier`, `NotifyRuleEngine`, `NotificationSystemSubscriberView`, `NotificationError`, `ParseConfigError`, `EventName`, `Arc`, and tracing. It is the bridge between S3 bucket notification XML/config parsing and event dispatch lookup.

Risks: missing ARN tolerance can allow rules for unavailable targets; dispatch must handle missing targets later. `has_subscriber` can return false if subscriber view and rule engine drift, so both updates must remain paired. Region-specific ARN list governs validation.

Test signals: Tokio tests verify empty state reports no subscriber and `remove_bucket_notification_config` clears a previously applied subscriber snapshot. Tests do not cover successful load validation, missing ARN warning behavior, or rule-engine confirmation after load.
