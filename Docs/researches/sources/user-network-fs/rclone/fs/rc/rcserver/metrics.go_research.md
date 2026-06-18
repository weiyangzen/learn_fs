# sources/user-network-fs/rclone/fs/rc/rcserver/metrics.go

## Purpose
This file implements the standalone Prometheus metrics HTTP server for rclone RC.

## Important APIs, Types, and Functions
- `MetricsStart(ctx, opt)` starts a metrics server only when `opt.MetricsHTTP.ListenAddr` is non-empty.
- `MetricsServer` wraps context, `libhttp.Server`, Prometheus handler, and RC options.
- `newMetricsServer` creates the HTTP server with metrics-specific config/auth/template options and registers `GET /metrics`.
- `Serve`, `Wait`, and `Shutdown` mirror the RC server lifecycle.

## Control Flow
Package init registers an accounting collector and fs HTTP metrics collectors with the default Prometheus registry, assigns `fshttp.DefaultMetrics`, and stores the default promhttp handler. `MetricsStart` updates job options, builds the server, and starts background serving.

## State and Persistence
Prometheus collectors are registered globally at init time. Runtime metrics are held in process memory via accounting and fshttp metrics. No filesystem persistence is used.

## Dependencies and Integration Points
It integrates `prometheus/client_golang`, `fs/accounting`, `fs/fshttp`, `rc.Options`, `jobs`, and `lib/http`. Metrics can also be served by the main RC server when `--rc-enable-metrics` is enabled; this file handles the separate metrics listener.

## Risks and Edge Cases
Global collector registration can panic if duplicate collectors are registered in the same process through unusual test/plugin loading. Metrics exposure depends on the configured metrics auth; an empty listener disables this server completely.

## Test Signals
`metrics_test.go` starts a metrics server on `localhost:0`, fetches `/metrics`, and asserts key rclone metric lines reflect `accounting.GlobalStats`.
