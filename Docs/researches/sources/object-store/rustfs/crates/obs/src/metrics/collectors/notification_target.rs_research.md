# sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification_target.rs

Purpose: emits per-notification-target delivery metrics: failed messages, queue length, and total messages.

Important APIs/types: `NotificationTargetStats` carries `failed_messages`, `queue_length`, `target_id`, `target_type`, and `total_messages`. `collect_notification_target_metrics(&[NotificationTargetStats])` emits three metrics per target.

Control flow: returns empty for no targets. For each target, allocates owned `target_id` and `target_type` labels and emits failed, queue, and total descriptors with both labels.

State/persistence: stateless conversion; target queues/counters live in the notification subsystem.

Dependencies/integration: uses `schema::notification_target` descriptors and label constants. The scheduler obtains snapshots via `rustfs_notify::notification_target_metrics().await` and maps them into this DTO.

Risks: target IDs may include user or configuration-derived strings, so cardinality and stability matter. Queue length is a gauge while failed/total are counters; resets on process restart are expected.

Test signals: test verifies three metrics for one webhook target and asserts `target_id`/`target_type` labels on total message output.
