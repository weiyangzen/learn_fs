# sources/sync-backup/kopia/internal/metrics/metrics_duration_distribution_test.go

Purpose: validates duration and size distribution creation, observation, snapshot state, reset behavior, label separation, nil safety, and Prometheus histogram export.

Important APIs/types/functions: `Registry.DurationDistribution`, `Registry.SizeDistribution`, `Distribution.Observe`, `Distribution.Snapshot`, `IOLatencyThresholds`, `ISOBytesThresholds`, and `mustFindMetric`.

Control flow: nil tests ensure nil registries/distributions are safe. Duration tests observe one or two values, verify Prometheus sample counts/sums in milliseconds, and assert min/max/sum/count/mean for labeled series. Size tests do the same for byte values and confirm `Snapshot(true)` resets local state.

State/persistence behavior: local distribution snapshots are resettable; Prometheus histograms are cumulative. Labels produce independent registry entries and Prometheus series.

Dependencies/integration: uses Prometheus client model and `testify/require`.

Risks/test signals: tests cover representative buckets and aggregates but not every threshold. They assume globally unique Prometheus metric names.
