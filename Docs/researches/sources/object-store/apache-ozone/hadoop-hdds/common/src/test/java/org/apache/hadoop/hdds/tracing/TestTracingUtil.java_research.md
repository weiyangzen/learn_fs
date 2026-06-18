# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingUtil.java

## Purpose
Tests `TracingUtil` initialization, proxy creation, span creation/export/import, child span execution, exception propagation, and text-map extraction.

## Important APIs, types, and functions
- Uses `TracingUtil.createProxy`, `initTracing`, `createActivatedSpan`, `exportCurrentSpan`, `importAndCreateSpan`, `executeInNewSpan`, `executeAsChildSpan`, and `TextExtractor`.
- Uses OpenTelemetry `Span`, `SpanContext`, and `Scope`.
- Reuses `TestTraceAllMethod.Service` and `ServiceImpl` fixtures.

## Control flow
The tests enable tracing in memory, initialize tracing services, create proxies, invoke normal and `@SkipTracing` methods, export W3C `traceparent` carriers, import parent contexts into child spans, run callbacks under new spans, and inspect text extractor behavior for empty or malformed carriers.

## State and persistence behavior
Tracing provider/context state is process-local. Span carriers are strings representing propagated trace context. No external collector or persistent trace store is required.

## Dependencies and integration points
The file covers HDDS tracing integration with OpenTelemetry context propagation and Java dynamic proxies.

## Risks and test signals
Risks include leaking spans into skipped methods, wrapping exceptions incorrectly, losing parent trace IDs, and accepting malformed carrier strings incorrectly. The suite signals core tracing correctness without depending on a live tracing backend.
