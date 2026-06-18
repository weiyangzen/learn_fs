# sources/user-network-fs/gcsfuse/tracing/otel_tracer.go

Purpose: OpenTelemetry-backed implementation of the gcsfuse tracing interface.

Important APIs/types/functions: `otelTracer`, attribute key globals, `StartSpan`, `StartServerSpan`, `EndSpan`, `RecordError`, `SetCacheReadAttributes`, `SetUploadAttributes`, `TraceUpload`, `PropagateTraceContext`, and `NewOTELTracer`.

Control flow: starts spans from the global OTel tracer, records errors and status, sets cache/upload attributes using a two-element `sync.Pool` slice, returns upload finishers that attach bytes/error attributes before ending the span, and copies a span from one context to another for propagation.

State/persistence behavior: holds a tracer and attribute slice pool in memory. Emitted spans are exported according to the global OpenTelemetry provider outside this file.

Dependencies/integration: implements `TraceHandle`; uses constants from `span_attributes.go` and tracer name from the package.

Risks/test signals: pooled slices are reused after `SetAttributes`, relying on OTel copying key-values synchronously. Tests cover span creation, server kind, error status, cache attributes, and context propagation; upload attributes are benchmarked but not unit-tested here.
