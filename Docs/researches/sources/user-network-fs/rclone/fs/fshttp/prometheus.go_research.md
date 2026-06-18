# sources/user-network-fs/rclone/fs/fshttp/prometheus.go

## Purpose
`prometheus.go` adds optional HTTP-level Prometheus instrumentation for `fshttp.Transport`. It counts responses by request host, HTTP method, and status code.

## Important APIs, types, and functions
`Metrics` contains a `StatusCode *prometheus.CounterVec`. `NewMetrics(namespace string)` creates the counter under subsystem `http` and name `status_code`. `DefaultMetrics` is a package-level hook copied into new transports. `Collectors` returns the collector set for registration. `onResponse` increments the counter and records status code `0` when there is no response.

## Control flow
Callers create metrics, register `Collectors`, and assign `DefaultMetrics` before constructing transports. `newTransport` captures the default metrics pointer. At the end of every `Transport.RoundTrip`, `t.metrics.onResponse(req, resp)` labels the observation with `req.Host`, `req.Method`, and `resp.StatusCode` or zero.

## State and persistence behavior
Metrics are in-memory Prometheus counters. `DefaultMetrics` is mutable process-global setup state; existing transports keep the pointer they were constructed with. There is no persistence beyond exporter scraping.

## Dependencies and integration points
The file depends on `github.com/prometheus/client_golang/prometheus` and integrates only through `fshttp.Transport.RoundTrip`. It is used by rclone processes that expose Prometheus metrics for backend HTTP activity.

## Risks and edge cases
Using raw `req.Host` may create high cardinality if requests span many hostnames. Nil metrics are intentionally a no-op. A nil response with an error becomes code `0`, which consumers must interpret as transport failure rather than an HTTP response.

## Test signals
There is no direct test in this subset. Indirect coverage comes from `RoundTrip` execution and any Prometheus integration tests elsewhere that register `DefaultMetrics`.

Source-read signal: reviewed complete local file (51 lines). Types observed: `Metrics`. Functions/methods observed: `NewMetrics`, `Collectors`, `onResponse`.
