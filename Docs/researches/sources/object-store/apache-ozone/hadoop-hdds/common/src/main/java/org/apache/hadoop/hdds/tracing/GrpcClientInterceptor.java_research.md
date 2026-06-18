# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/GrpcClientInterceptor.java

## Purpose
gRPC client interceptor that propagates the current tracing context in outbound metadata.

## Important APIs and types
Defines metadata key `TRACING_HEADER` named `"Tracing"`. `interceptCall` wraps the client call and merges a metadata entry containing `TracingUtil.exportCurrentSpan()` before starting the call.

## Control flow and state
The interceptor is stateless. It sends an empty string when no valid span exists because `exportCurrentSpan` returns the null-span sentinel.

## Dependencies and integration points
Uses shaded Ratis gRPC APIs and `TracingUtil`. It pairs with `GrpcServerInterceptor`, which reads the same header.

## Risks and test signals
Tests should verify header insertion with valid and invalid current spans, merge behavior with existing metadata, and compatibility with the server interceptor. Header name changes break propagation.
