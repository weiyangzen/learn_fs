## sources/user-network-fs/gcsfuse/internal/monitor/traceexporter.go

### Purpose
`traceexporter.go` bootstraps OpenTelemetry tracing for gcsfuse using configured exporters, resource attribution, and sampling ratio.

### Important APIs, Types, And Functions
Public entry point `SetupTracing` calls `newTraceProvider`. `exporterFactory` abstracts exporter creation. Exporter helpers are `newStdoutTraceExporter` and `newGCPCloudTraceExporter`.

### Control Flow
`SetupTracing` creates a trace provider and installs it globally if creation succeeds. `newTraceProvider` maps configured exporter names `stdout` and `gcpexporter` to factories, adds each initialized exporter as a batcher, obtains the same resource shape used by metrics, applies a `TraceIDRatioBased` sampler, constructs a SDK tracer provider, and returns its shutdown function.

### State, Persistence, And Dependencies
State is the global OTel tracer provider and exporter batch processors. Output goes to stdout or Google Cloud Trace. Dependencies include OTel trace SDK, stdout trace exporter, GCP Cloud Trace exporter, config, common shutdown type, logger, and `getResource`.

### Integration Points
Tracing shares service name/version/mount ID resource identity with metrics. It depends on config-provided exporter names, GCP project ID, and sampling ratio.

### Risks
Unknown exporter names are silently ignored, which can hide configuration mistakes. Resource detection errors fail tracing setup. Multiple calls replace the global provider. Invalid sampling ratios are not validated in this file.

### Test Signals
No direct tests are present. Valuable tests would cover exporter selection, unknown names, GCP project option, resource failure, and sampler ratio propagation.
