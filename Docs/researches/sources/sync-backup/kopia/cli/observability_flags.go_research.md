<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags.go -->
# sources/sync-backup/kopia/cli/observability_flags.go

## Purpose
Implements process-wide diagnostics flags for metrics serving, Prometheus push gateway, OTLP tracing, allocator stats, metrics-on-exit, and profiling coordination.

## Important APIs, Types, And Functions
Important symbols are `observabilityFlags`, `metricsPushFormats`, `setup`, `initialize`, `run`, `start`, `mkSubdirectories`, `maybeStartListener`, `maybeStartMetricsPusher`, `maybeStartTraceExporter`, `stop`, `pushPeriodically`, and `pushOnce`.

## Control Flow
PreAction computes a per-command diagnostics subdirectory. `run` starts observability, starts profiling, optionally creates a root trace span, runs the command, then stops profilers/exporters/pushers and writes metrics if requested. Metrics listener and pusher run in goroutines; pusher sends initial, periodic, and final pushes.

## State And Persistence Behavior
Persistent state can include diagnostics directories, `kopia-metrics.prom`, pprof files via `profile.go`, and remote metrics/traces. Runtime state includes pusher channels/waitgroup and OTLP tracer provider.

## Dependencies And Integration Points
Integrates Kingpin, Prometheus gatherer/listener/push, Gorilla mux, pprof handlers, OpenTelemetry OTLP gRPC, repo build metadata, clock, gather stats, and `profileFlags`.

## Risks And Edge Cases
`http.ListenAndServe` errors are ignored, so listener bind failures can be silent. Push failures are debug logs only. Grouping parsing requires `name:value`. Trace exporter startup can fail commands. Output directory creation is validated only for requested save/profile modes.

## Test Signals
Tests cover push URL/grouping/auth/body, invalid grouping, OTLP flag tolerance, and metrics file creation. Additional tests should cover pprof listener conflicts and trace startup failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags.go -->
