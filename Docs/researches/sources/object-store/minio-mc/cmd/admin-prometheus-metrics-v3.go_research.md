# sources/object-store/minio-mc/cmd/admin-prometheus-metrics-v3.go

## Purpose
Provides v3 Prometheus metrics path construction, validation, and fetching for `mc admin prometheus metrics`.

## Important APIs, types, and functions
`metricsV3Flags` defines `--bucket`. `metricsV3SubSystems` and `bucketMetricsSubSystems` validate subsystem names. `getMetricsV3Path`, `validateV3Args`, and `printPrometheusMetricsV3` implement the behavior.

## Control flow
`getMetricsV3Path` builds `/minio/metrics/v3`, optionally adds `/bucket`, subsystem, and bucket name. `validateV3Args` rejects unknown subsystems and ensures bucket metrics are only requested with supported subsystems. `printPrometheusMetricsV3` fetches the URL and prints the body on HTTP 200.

## State and persistence behavior
The file is read-only and stateless. It streams metrics from the server without local persistence.

## Dependencies and integration points
It integrates the shared metrics request struct, `fetchMetrics`, `prometheusMetricsReader`, CLI bucket flag, HTTP status handling, and MinIO set utilities.

## Risks and edge cases
Bucket names are inserted into the path without URL escaping in this helper, so unusual bucket strings rely on prior CLI/server constraints. Non-200 responses return only status text. Empty subsystem means all v3 metrics unless a bucket is specified.

## Test signals
Tests should cover path construction for all/bucket/subsystem variants, invalid subsystem messages, bucket-without-subsystem rejection, unsupported bucket subsystem rejection, HTTP 200 streaming, and non-200 errors.
