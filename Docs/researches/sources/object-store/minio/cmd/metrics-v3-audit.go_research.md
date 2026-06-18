# sources/object-store/minio/cmd/metrics-v3-audit.go

Purpose: Exposes v3 audit logger target metrics for failed messages, queue length, and total sent messages.

Important APIs/types/functions: Defines `auditFailedMessages`, `auditTargetQueueLength`, `auditTotalMessages`, and label `target_id`. `loadAuditMetrics` reads `logger.CurrentStats()` and stores three metrics per target in `MetricValues`.

Control flow: On scrape, the loader iterates the current audit stats map. For each target id it builds the `target_id` label pair and sets failed, queue, and total values.

State and persistence behavior: The loader is stateless; state is maintained by the logger subsystem. Queue length is a gauge-like live value, while totals and failures are counters since process start.

Dependencies and integration points: Depends on `github.com/minio/minio/internal/logger` and the v3 metrics framework. It integrates with audit webhook/logging targets and is surfaced by the v3 collection tree.

Risks: Target ids become labels, so a deployment with many dynamic audit targets could increase cardinality. The cache parameter is unused, so every scrape reads current logger stats directly.

Test signals: No direct tests in this subset.
