# sources/object-store/minio-mc/cmd/admin-prometheus-metrics.go

## Purpose
Implements `mc admin prometheus metrics`, fetching raw Prometheus metrics from MinIO v2 or v3 endpoints and optionally converting them to JSON.

## Important APIs, types, and functions
Key symbols include `metricsFlags`, `metricsV2SubSystems`, `adminPrometheusMetricsCmd`, `prometheusMetricsReq`, `checkSupportMetricsSyntax`, `fetchMetrics`, `validateV2Args`, `printPrometheusMetricsV2`, `prometheusMetricsReader`, and `mainSupportMetrics`.

## Control flow
The handler validates target plus optional metric type, resolves local alias config, obtains a Prometheus bearer token, builds a request object, and dispatches to v2 or v3 printing. V2 defaults to cluster metrics and rejects v3-only flags. Successful responses stream the body; JSON mode parses Prometheus results before marshaling.

## State and persistence behavior
No state is modified. The command reads local alias configuration and remote metrics, and streams data to stdout.

## Dependencies and integration points
It uses `httpClient`, bearer-token auth, `madmin.ParsePrometheusResults`, global JSON mode, v3 helpers, v2 subsystem validation, and shared fatal/probe error handling.

## Risks and edge cases
Metrics streaming writes directly to stdout in string mode, making output handling unusual for `String`. Non-200 responses lose response body details. Token generation failures stop the command before any HTTP call.

## Test signals
Tests should cover syntax, alias validation, missing alias config, v2 default and invalid subsystem, v3 dispatch, bearer header injection, JSON parse failures, non-200 status errors, and raw body streaming.
