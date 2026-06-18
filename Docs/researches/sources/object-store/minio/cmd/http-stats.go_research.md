# sources/object-store/minio/cmd/http-stats.go

## Purpose

`http-stats.go` defines the in-memory counters used by MinIO to track aggregate network bytes, per-bucket S3 bytes, process-wide HTTP API counts, bucket-level HTTP API counts, request queue depth, rejected requests, errors, cancellations, and request duration histograms. It is part of the observability surface consumed by server info/admin APIs and Prometheus metrics.

## Important APIs, Types, And Control Flow

`connStats` owns atomic byte counters for internode and S3 traffic. Its `inc*` methods use `atomic.AddUint64`, its `get*` methods use `atomic.LoadUint64`, and `toServerConnStats` materializes the public stats DTO. `bucketConnStats` adds per-bucket S3 in/out byte accounting behind an `RWMutex` and returns copies from `getS3InOutBytes` and `getBucketS3InOutBytes` so callers do not share mutable map state.

`HTTPAPIStats` is a mutex-protected map from API name to count with `Inc`, `Dec`, `Get`, and `Load`. `Load(toLower)` copies keys and optionally normalizes API names. `HTTPStats` embeds several `HTTPAPIStats` values for current, total, error, 4xx, 5xx, and canceled request counts. `toServerHTTPStats` snapshots the counters, notably using `atomic.SwapUint64` for `s3RequestsIncoming`, so that field reports and resets interval-style arrivals while other totals remain cumulative. `updateStats` records total requests, Prometheus TTFB duration, HTTP 499 cancellations, and 4xx/5xx buckets.

`bucketHTTPStats` stores a map of bucket name to `bucketHTTPAPIStats`. `updateHTTPStats(bucket, api, nil)` increments active bucket requests; the later call with a `ResponseRecorder` decrements active requests, increments total, classifies status, and observes `bucketHTTPRequestsDuration`.

## State, Dependencies, Integration, Risks, And Tests

State is entirely process-local and reset on restart, except that admin callers may periodically read and persist snapshots elsewhere. Dependencies include `internal/http.ResponseRecorder`, `net/http`, `sync/atomic`, `sync.RWMutex`, and Prometheus collectors. Integration points are S3 request handlers, bucket deletion cleanup, server-info serialization, and metrics endpoints. Risks include paired active-request increments/decrements getting out of balance when middleware paths diverge, byte counters wrapping, `s3RequestsIncoming` being destructive on read, and bucket stats growing until explicit delete. `http-tracer_test.go` adds race-oriented tests for `HTTPStats`, `HTTPAPIStats`, and `bucketHTTPStats`, giving a direct signal that the map locks are required for concurrent request/update/read paths.
