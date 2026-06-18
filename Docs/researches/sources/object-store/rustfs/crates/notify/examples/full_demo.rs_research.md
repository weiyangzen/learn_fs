# sources/object-store/rustfs/crates/notify/examples/full_demo.rs

Purpose: end-to-end notification demo that initializes the global notification system, configures webhook/MQTT-style targets, removes a target, loads bucket rules, and sends a test event.

Important APIs/types/functions: uses `initialize`, `notification_system`, `Config`, `KV`, `KVS`, notify subsystem constants, `BucketNotificationConfig`, `Event::new_test_event`, `TargetID`, and `EventName::ObjectCreatedPut`.

Control flow: initializes logging, obtains or creates the global notification system, constructs webhook KVS and an MQTT KVS, writes config into `system.config`, calls `system.init`, checks active targets, removes the MQTT target, builds bucket notification config with webhook and MQTT rules, loads it for `my-bucket`, sends an event, then waits for delivery/logging.

State and persistence: mutates in-memory global notification system config and target/rule state. Queue directories point under a project-root-relative deploy/logs path, so real target backends may persist queued events there.

Dependencies/integration: integrates rustfs-config target settings, rustfs-notify global system APIs, rustfs-utils project-root discovery, S3 event names, target ARNs, Tokio, and tracing.

Risks: contains assertions about active target count that may be stale because MQTT insertion is commented while the log text says webhook and MQTT. It assumes a local webhook server at `127.0.0.1:3020` and optional MQTT environment. Hard-coded credentials and paths make it demo-only.

Test signals: not a test, but executable as an example. It exercises target removal and missing-target behavior during event dispatch.
