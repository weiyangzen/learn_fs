# sources/object-store/minio/cmd/metrics-v3-api.go

Purpose: Defines v3 API and bucket API metrics for S3 HTTP requests, TTFB histograms, rejected requests, and network byte counters.

Important APIs/types/functions: Metric descriptors include `apiRejected*`, `apiRequests*`, `apiRequestsTTFBSecondsDistribution`, and `apiTraffic*` variants. `loadAPIRequestsHTTPMetrics`, `loadAPIRequestsTTFBMetrics`, and `loadAPIRequestsNetworkMetrics` populate node-level S3 metrics. `loadBucketAPIHTTPMetrics` and `loadBucketAPITTFBMetrics` populate bucket-scoped metrics for explicitly requested buckets.

Control flow: Node HTTP metrics read `globalHTTPStats.toServerHTTPStats(false)`, set global rejection and queue counters with `type=s3`, then iterate per-API maps for inflight, totals, errors, 4xx, 5xx, and canceled counts. TTFB loaders call `MetricValues.SetHistogram`, renaming the `api` label to `name`. Bucket HTTP metrics first require a non-empty bucket list, read bucket connection stats and per-bucket HTTP stats, and set labels `bucket`, `name`, and `type`.

State and persistence behavior: Stateless loader code over live counters. Histogram state lives in global Prometheus histogram vectors. Bucket metrics are request-filtered in v3 rather than globally capped as in v2.

Dependencies and integration points: Uses `MetricValues`, `NewCounterMD`, `NewGaugeMD`, `SetHistogram`, `globalHTTPStats`, `globalBucketHTTPStats`, `globalBucketConnStats`, `globalConnStats`, `httpRequestsDuration`, and `bucketHTTPRequestsDuration`. Consumed by v3 metric group registration and `metrics-v3-handler.go`.

Risks: Label naming changes from v2 (`api` to `name`) can affect dashboards. Bucket traffic descriptor help text appears swapped relative to variable names: sent descriptor says received and received descriptor says sent. Bucket metrics produce nothing if the v3 handler does not pass bucket filters.

Test signals: No direct tests in this subset. Indirect coverage may come from generic v3 metric group tests elsewhere and v2 histogram tests for shared histogram conversion concepts.
