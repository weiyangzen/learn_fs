# sources/object-store/minio/cmd/metrics-v3-logger-webhook.go

Purpose: Exposes v3 metrics for system and audit logger webhook targets.

Important APIs/types/functions: Defines `webhookQueueLength`, `webhookTotalMessages`, `webhookFailedMessages`, labels `name` and `endpoint`, and `loadLoggerWebhookMetrics`.

Control flow: The loader appends `logger.SystemTargets()` and `logger.AuditTargets()`, then for each target sets failed messages, queue length, and total messages with target name and endpoint labels.

State and persistence behavior: Stateless over logger target stats. Queue length is live, totals/failures are process-lifetime counters.

Dependencies and integration points: Depends on MinIO internal logger target APIs and v3 metrics descriptors. It integrates with alerting on webhook delivery backlog or failures.

Risks: Endpoint values are labels and may include high-cardinality or sensitive deployment details. Target health/online status is not exposed here, unlike the legacy v2 webhook metrics that included online state.

Test signals: No direct tests in this subset.
