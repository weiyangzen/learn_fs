# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcServerInterceptor.java

## Purpose
gRPC server interceptor that imports a propagated tracing context and creates an active span for message handling.

## Important APIs and types
`interceptCall` wraps the server listener. `onMessage` calls `TracingUtil.importAndCreateSpan` with the full method name and the client tracing header, makes the span current while delegating to the real listener, and ends the span.

## Control flow and state
The interceptor is stateless. It creates one span per received message rather than per call lifecycle event.

## Dependencies and integration points
Pairs with `GrpcClientInterceptor` and uses OpenTelemetry `Span`/`Scope` plus shaded Ratis gRPC server APIs.

## Risks and test signals
Tests should cover propagated and absent headers, span closure when delegate throws, and multi-message RPC behavior. Exceptions from `super.onMessage` still end the span because of `finally`.
