# sources/object-store/rustfs/crates/ecstore/src/rpc/context_propagation.rs

Purpose: This file provides the observability propagation glue used by HTTP and tonic internode RPCs. It injects OpenTelemetry trace context and a stable request id into outbound HTTP headers or tonic metadata so downstream peers can correlate logs and spans.

Important APIs/types/functions: `HttpHeaderInjector` and `MetadataInjector` implement OpenTelemetry `Injector` for `http::HeaderMap` and `tonic::metadata::MetadataMap`. `current_trace_id` reads the current tracing span's OpenTelemetry context and returns a valid trace id when available. `fallback_request_id` creates a short `req-<uuid-prefix>` identifier. `propagated_request_id` prefers `trace-<trace_id>` and falls back to the generated request id. Public crate functions are `inject_trace_context_into_http_headers`, `inject_request_id_into_http_headers`, `inject_trace_context_into_metadata`, and `inject_request_id_into_metadata`; `REQUEST_ID_HEADER` is re-exported from `rustfs_utils`.

Control flow: Trace injection obtains `Span::current().context()` and calls the global text-map propagator with the appropriate injector. Each injector validates header/metadata keys and values before insertion and silently skips invalid output from the propagator. Request-id injection first checks whether the destination already contains `x-request-id`; if it does, the upstream value is preserved. Otherwise it derives a trace-backed or fallback id and inserts it if the value is valid for the destination map.

State and persistence behavior: The module has no persistent state. Its runtime behavior depends on the process-global OpenTelemetry propagator and current tracing subscriber/span. Request ids generated without a valid trace id are random UUID-derived values and are not stored.

Dependencies and integration points: It is called by `http_auth::build_auth_headers` for HTTP data-plane requests and by `client::TonicSignatureInterceptor` for gRPC control-plane requests. It depends on `http`, `tonic`, `opentelemetry`, `tracing`, `tracing-opentelemetry`, `uuid`, and `rustfs_utils` header constants.

Risks: Injection failures are intentionally ignored, so malformed propagator output can silently drop trace context. Fallback request ids use only the first eight UUID characters, which is compact for logs but has less uniqueness than a full UUID. The module only injects outbound context; extraction/continuation for inbound peer handlers must be implemented elsewhere for full distributed tracing.

Test signals: Inline tests cover preserving existing request ids, deriving request ids from a supplied trace id for both HTTP and tonic metadata, and fallback `req-` ids when no trace context is active. Tests construct OpenTelemetry SDK subscribers and parent span contexts but do not verify full cross-process extraction.
