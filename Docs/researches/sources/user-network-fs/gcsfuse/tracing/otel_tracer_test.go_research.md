# sources/user-network-fs/gcsfuse/tracing/otel_tracer_test.go

Purpose: unit tests for the OpenTelemetry tracer implementation.

Important APIs/types/functions: `TestOtelTracer_StartEndSpan`, `TestOtelTracer_StartServerSpan`, `TestOtelTracer_RecordError`, `TestOtelTracer_SetCacheReadAttributes`, and `TestOtelTracer_PropagateTraceContext`.

Control flow: each test installs an SDK tracer provider with a span recorder, creates `NewOTELTracer`, performs a tracing operation, ends spans where needed, and asserts recorder contents.

State/persistence behavior: mutates the global OTel tracer provider for each test; all span data is in-memory.

Dependencies/integration: uses `tracetest.SpanRecorder`, `sdktrace.TracerProvider`, OTel attributes/codes, and `testify/assert`.

Risks/test signals: tests do not reset the global provider to its previous value, so package-level parallelism would need care. Upload-specific attributes and `TraceUpload` finisher behavior are not directly asserted.
