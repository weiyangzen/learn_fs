## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonS3TraceContextRequestHandler.java

Purpose: AWS SDK request handler that injects W3C trace context headers into outgoing S3 requests from Freon.

Important APIs/types/functions: extends `RequestHandler2` and overrides `beforeRequest(Request<?>)`.

Control flow: before an AWS SDK request is sent, checks whether the current OpenTelemetry span context is valid. If valid, uses `W3CTraceContextPropagator.inject` with the request as carrier and `addHeader` as setter.

State and persistence behavior: stateless. It mutates outgoing request headers only.

Dependencies and integration points: integrates AWS Java SDK request handling with OpenTelemetry tracing. Intended for Freon S3 workloads so S3 Gateway spans can attach to Freon task spans.

Risks: no-op without active valid span; assumes AWS request headers preserve W3C trace fields; adding duplicate headers depends on AWS SDK request behavior.

Test signals: unit/integration tests can install the handler under an active span and assert `traceparent` header propagation.
