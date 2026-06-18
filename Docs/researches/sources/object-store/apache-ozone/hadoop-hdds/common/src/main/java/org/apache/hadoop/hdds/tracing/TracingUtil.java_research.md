# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingUtil.java

## Purpose
Central OpenTelemetry utility for initializing tracing, exporting/importing span context, proxy tracing, span execution helpers, and HTTP/gRPC header extraction helpers.

## Important APIs and types
Initialization APIs are `initTracing`, `reconfigureTracing`, and internal `initialize`/`shutdownTracing`. Context propagation APIs are `exportCurrentSpan`, `importAndCreateSpan`, `TextExtractor`, and `HttpHeaderGetter`. Execution APIs are `executeInNewSpan`, `executeAsChildSpan`, `createActivatedSpan`, `createActivatedSpanFromW3cHttpHeaders`, and `getActiveSpan`. `createProxy` wraps interfaces with `TraceAllMethod` when tracing is enabled.

## Control flow and state
Static state tracks initialization, current `Tracer`, and `SdkTracerProvider`. Initialization is synchronized and no-ops when disabled or already initialized. It creates an OTLP gRPC exporter, simple span processor, service-name resource, and either a trace-ratio sampler or `SpanSampler` with parsed per-span settings. Reconfigure shuts down the old provider first.

`exportCurrentSpan` returns an empty string when no valid span exists, otherwise injects W3C trace context into a semicolon-separated `key=value;` carrier. `importAndCreateSpan` starts a root span for null/empty carriers or extracts a parent context using `TextExtractor`. Execution helpers mark spans error on exceptions and always end spans. HTTP header activation uses W3C HTTP headers and returns a no-op closeable when config is null or disabled.

## Dependencies and integration points
Depends on OpenTelemetry API/SDK/exporter, HDDS configuration, Ratis checked functional interfaces, dynamic proxies, and tracing config/sampler classes. Used by container protocol calls, gRPC interceptors, and service implementations.

## Risks and test signals
Tests should cover idempotent initialization, disabled tracing no-op behavior, reconfiguration shutdown, exporter construction failure cleanup, context export/import, malformed carrier parsing, span sampling config parsing, exception status marking, no-op HTTP activation, and proxy creation. `TextExtractor` caches parsed carrier data in an instance, so it should not be reused across different carriers. Simple span processing exports synchronously and may affect latency.
