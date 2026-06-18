## sources/user-network-fs/gcsfuse/internal/monitor/bucket.go

### Purpose
`bucket.go` wraps a `gcs.Bucket` to record GCS operation counts, operation latencies, reader lifecycle counts, and read-byte counts.

### Important APIs, Types, And Functions
Public functions are `NewMonitoringBucket` and `CaptureMultiRangeDownloaderMetrics`. Internal helpers include `recordRequest`, `setupReader`, `recordReader`, and `newMonitoringReadCloser`. `monitoringBucket` implements `gcs.Bucket`; `monitoringReadCloser` wraps `gcs.StorageReader`.

### Control Flow
Each bucket method records `startTime`, delegates to the wrapped bucket, then calls `recordRequest` with the appropriate `metrics.GcsMethod`. Successful reader creation wraps the storage reader so open count is incremented immediately, reads add bytes to `GcsReadBytesCount`, and close increments closed count after a successful close. Metadata-only methods such as `Name`, `BucketType`, and `GCSName` simply delegate.

### State, Persistence, And Dependencies
State is the wrapped bucket and a `metrics.MetricHandle`; metrics are exported through the metric subsystem rather than local storage. Dependencies include `internal/storage/gcs`, `metrics`, `time`, `context`, and Cloud Storage read handles.

### Integration Points
This wrapper composes with storage, caching, throttling, and monitoring setup. It instruments both object and folder APIs, including hierarchical namespace methods and multi-range downloader creation.

### Risks
Requests are counted regardless of success, which is intentional but should match dashboard semantics. A reader close error prevents the closed count from being incremented, potentially making open/close gauges diverge. Multi-range downloader byte-level reads are not wrapped here; only creation metrics are recorded unless external code calls `CaptureMultiRangeDownloaderMetrics`.

### Test Signals
No direct tests are in this shard. Valuable tests would use a fake metric handle to verify method labels, latency calls on error and success, reader byte counts, and close-error behavior.
