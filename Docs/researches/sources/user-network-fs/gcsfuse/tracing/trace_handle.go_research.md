# sources/user-network-fs/gcsfuse/tracing/trace_handle.go

Purpose: declares the tracing abstraction used by gcsfuse to record spans without coupling call sites to a specific OpenTelemetry implementation. It also defines the instrumentation library name constant `name = "cloud.google.com/gcsfuse"`.

Important APIs/types/functions: `TraceHandle` includes span lifecycle methods (`StartSpan`, `StartServerSpan`, `EndSpan`, `RecordError`), optimized attribute setters (`SetCacheReadAttributes`, `SetUploadAttributes`), `TraceUpload` for deferred upload finalization, and `PropagateTraceContext`. The comments explain an allocation-sensitive API choice: callers pass primitive values so a noop tracer can avoid attribute construction.

Control flow/state: this file is pure interface definition. Concrete behavior is supplied by noop or OTEL implementations.

Dependencies/integration: depends on `context` and `go.opentelemetry.io/otel/trace`. Risks include interface churn affecting all tracers, nil span handling in implementations, and pointer-based `TraceUpload` inputs requiring callers to keep bytes/error variables live until the finisher runs. Tests should validate both noop and OTEL implementations against this contract.
