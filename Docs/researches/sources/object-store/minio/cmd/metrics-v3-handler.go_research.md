# sources/object-store/minio/cmd/metrics-v3-handler.go

Purpose: Implements the HTTP server for v3 metrics, including path-based collector selection, listing mode, bucket path parsing, authentication wrapping, and Prometheus handler options.

Important APIs/types/functions: `metricsV3Server` holds a Prometheus registry, promhttp options, auth wrapper, and `metricsV3Collection`. `newMetricsV3Server` constructs metric groups and initializes global collector path listing once. `metricDisplay` formats descriptor metadata. `listMetrics` returns JSON or markdown-table text for metrics under a path. `handle` maps request paths to gatherers and injects bucket filters. `ServeHTTP` parses mux path variables and query parameters, wraps tracing, and applies auth.

Control flow: Server construction creates a registry and metric group collection. Request handling extracts `pathComps`, detects `?list`, and parses `/bucket/.../<bucket>` paths by stripping the final bucket component from the collector path. Non-list requests collect all descendant paths and gatherers. For bucket metric groups, the handler sets the requested bucket list under a group lock for the duration of collection. If no matching gatherers or listing data exist, it returns 404. Otherwise it delegates to `promhttp.HandlerFor`.

State and persistence behavior: Runtime state includes a registry, metric group collection, promhttp options, global collector path cache guarded by `sync.Once`, and temporary bucket lists stored in bucket metric groups under locks. There is no durable persistence.

Dependencies and integration points: Depends on `newMetricGroups`, `metricsV3Collection`, `MetricsGroup.LockAndSetBuckets`, mux route variables, Prometheus promhttp, OpenMetrics environment config, tracing context, and the auth middleware supplied by the caller.

Risks: Bucket selection by last path component assumes bucket names do not require additional path escaping in this route. `listMetrics` checks request `Content-Type` instead of `Accept`, which may surprise clients asking for JSON. Bucket metric groups return nothing unless buckets are explicitly supplied. `MaxRequestsInFlight` is set to 2, so slow collectors can throttle concurrent scrapes.

Test signals: No direct tests in this subset.
