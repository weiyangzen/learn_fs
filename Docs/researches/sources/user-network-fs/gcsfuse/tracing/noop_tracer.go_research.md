# sources/user-network-fs/gcsfuse/tracing/noop_tracer.go

Purpose: no-op implementation of the tracing interface for deployments or tests without active tracing.

Important APIs/types/functions: `noopTracer`, `emptyFinisher`, methods implementing span start/end, server span, error recording, cache/read attributes, upload attributes, `TraceUpload`, `PropagateTraceContext`, and `NewNoopTracer`.

Control flow: every method returns the input context, noop span, empty finisher, or no-op side effect. Context propagation deliberately returns the new context unchanged.

State/persistence behavior: no state or persistence.

Dependencies/integration: implements `TraceHandle` using OpenTelemetry `noop.Span`.

Risks/test signals: no direct tests in this file, but benchmarks include noop behavior. It should remain allocation-light and semantically inert.
