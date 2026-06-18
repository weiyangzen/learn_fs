# sources/user-network-fs/gcsfuse/tracing/span_attributes.go

Purpose: centralizes tracing span attribute key strings.

Important APIs/types/functions: constants `IS_CACHE_HIT`, `BYTES_READ`, `BYTES_UPLOADED`, and `OBJECT_NAME`.

Control flow: no executable flow.

State/persistence behavior: no state; constants define exported instrumentation key names.

Dependencies/integration: consumed by `otel_tracer.go` and tests to set/assert attributes.

Risks/test signals: changing these constants changes telemetry schema and test expectations, so they are integration-facing API surface.
