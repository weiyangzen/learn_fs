<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go

## Purpose

This Go test file validates OpenTelemetry GCS metrics emitted by gcsfuse filesystem operations against a monitored fake bucket. It covers request counts and latencies, download/read byte counters, reader lifecycle counters, cache-hit behavior, parallel download accounting, and retry categorization.

## Important APIs, Types, and Functions

`fakeBucketManagerWithMetrics` is a test `gcsx.BucketManager` that wraps fake buckets in `monitor.NewMonitoringBucket` and `gcsx.NewContentTypeBucket`, making storage calls produce GCS metrics. `createTestFileSystemWithMonitoredBucket` installs an OpenTelemetry manual reader, constructs `metrics.NewOTelMetrics`, configures `fs.ServerConfig`, optionally enables file cache or sparse chunk cache, and returns the fake bucket, FUSE filesystem, metric handle, and manual reader.

The tests exercise `server.LookUpInode`, `GetInodeAttributes`, `CreateFile`, `SyncFile`, `OpenFile`, and `ReadFile`, then assert metrics through `metrics.VerifyCounterMetric` and `metrics.VerifyHistogramMetric`.

## Control Flow

Each test builds an isolated monitored filesystem, seeds fake GCS objects when needed, performs a FUSE operation sequence, waits for metric processing, and reads the manual OpenTelemetry reader. Lookup tests expect `StatObject` increments from directory, file, and attribute refresh paths. Write tests create a local file handle and rely on `SyncFile` to trigger `CreateObject`. Read tests route through buffered read, file cache, or parallel download code paths and verify corresponding `read_type` attributes.

## State and Persistence Behavior

State is test-local: the global OpenTelemetry meter provider is replaced and restored with `t.Cleanup`, temporary cache directories are removed, fake bucket contents hold test objects, and metric data lives in the manual reader. There is no durable repository state. The tests depend on asynchronous metric export timing via `waitForMetricsProcessing`.

## Dependencies and Integration Points

The file integrates `internal/fs`, `internal/fs/wrappers`, `internal/monitor`, `internal/storage/fake`, `storageutil`, `metrics`, `tracing`, FUSE ops, and OpenTelemetry SDK metric readers. It specifically verifies that filesystem operations, storage wrappers, read managers, file cache, parallel downloads, and retry helpers all feed the public GCS metric instruments.

## Risks and Edge Cases

The expected counts encode details of lookup and read implementation. Changes to attribute refresh, wrapper layering, cache behavior, chunk sizing, or OpenTelemetry async collection can make assertions fail even if user-visible behavior is correct. The file cache test assumes the second read is served locally, and the parallel download test assumes 1 MiB chunks for a 5 MiB file.

## Test Signals

Coverage includes `gcs/request_count`, `gcs/request_latencies`, `gcs/download_bytes_count`, `gcs/read_count`, `gcs/reader_count`, `gcs/read_bytes_count`, and `gcs/retry_count`, including retry categories for HTTP 429 and `context.DeadlineExceeded`. It is a metrics regression suite rather than a production implementation file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go -->
