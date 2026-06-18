# sources/object-store/rustfs/crates/notify/examples/full_demo_one.rs

Purpose: dynamic notification configuration demo focused on adding and removing targets while the notification system is running.

Important APIs/types/functions: same core APIs as `full_demo.rs`, plus `set_target_config`, `remove_target_config`, and `remove_bucket_notification_config`.

Control flow: initializes or retrieves the global notification system, configures and initializes a webhook target, sleeps, dynamically adds an MQTT target via `set_target_config`, creates bucket rules for webhook and MQTT targets, sends an ObjectCreatedPut test event, removes the webhook target config, removes bucket notification config, and exits after a short delay.

State and persistence: mutates global notification config, active targets, bucket rule state, and queue directories under deploy/logs. Event payloads are in-memory unless target queues persist them.

Dependencies/integration: ties together config subsystem constants, notification system runtime APIs, target IDs, S3 event names, Tokio sleeps, and tracing logs. It expects a local webhook endpoint and MQTT broker to be useful beyond compilation.

Risks: `remove_target_config("notify_webhook", "1")` hard-codes strings instead of using imported constants/default target, which may drift. External services and paths are assumed. Credentials are example values.

Test signals: not a unit test; it is an integration-style example for manual or CI example compilation. It gives coverage of dynamic add/remove flows absent from `bucket_config_manager` unit tests.
