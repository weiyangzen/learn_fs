# sources/sync-backup/kopia/internal/metrics/metrics_thresholds.go

Purpose: defines reusable bucket thresholds for size, IO latency, and CPU latency distributions plus the helper that maps values to bucket indexes.

Important APIs/types/functions: `Thresholds[T]`, `ISOBytesThresholds`, `IOLatencyThresholds`, `CPULatencyThresholds`, and `bucketForThresholds`.

Control flow: threshold globals provide sorted bucket boundary slices, Prometheus scaling factors, and metric-name suffixes. `bucketForThresholds` performs binary search and returns the first index whose threshold is greater than or equal to the observed value, or the overflow index after the last threshold.

State/persistence behavior: thresholds are process-global constants in practice. Bucket layout affects serialized distribution bucket counters and Prometheus histogram buckets, so changes alter metric interpretation.

Dependencies/integration: used by `metrics_distribution.go` constructors and tests. Duration thresholds use `time.Duration` values.

Risks/test signals: threshold slices must stay sorted for binary search correctness. Changing thresholds can break historical comparison of bucket counters unless versioned elsewhere.
