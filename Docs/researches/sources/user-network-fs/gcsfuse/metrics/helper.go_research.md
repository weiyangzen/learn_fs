## sources/user-network-fs/gcsfuse/metrics/helper.go

Purpose: Convenience helper for recording paired GCS read metrics.

Important APIs/types/functions: `CaptureGCSReadMetrics(mh MetricHandle, readType ReadType, downloadBytes int64)`.

Control flow: increments read count by one and download byte count by the provided byte count for the same read type.

State and persistence behavior: no local state; emits metric side effects through `MetricHandle`.

Dependencies and integration points: used by read paths to avoid duplicating two metric calls.

Risks: assumes `mh` is non-nil. It records download bytes but not `GcsReadBytesCount`, so callers must understand which metric pair is intended.

Test signals: no direct test in this subset.
