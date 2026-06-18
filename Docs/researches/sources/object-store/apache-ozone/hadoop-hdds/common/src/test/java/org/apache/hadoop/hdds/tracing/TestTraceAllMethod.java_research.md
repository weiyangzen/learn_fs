# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTraceAllMethod.java

## Purpose
Tests tracing proxy behavior for interfaces annotated to trace all methods, including default methods and unknown methods.

## Important APIs, types, and functions
- Defines a `Service` interface and `ServiceImpl` test implementation with normal, skipped, throwing, and default methods.
- Uses OpenTelemetry `Span.current()` to detect active span state.
- Tests `testUnknownMethod` and `testDefaultMethod` through `TracingUtil.createProxy` behavior.

## Control flow
Proxy instances invoke service methods through tracing utilities. The implementation records whether a span is active, while tests assert default method dispatch and behavior when a method is not matched to a concrete implementation path.

## State and persistence behavior
State is limited to the implementation's boolean span-active observation. No persistence.

## Dependencies and integration points
The file provides fixtures reused by `TestTracingUtil` and guards dynamic proxy tracing around Java interface/default method semantics.

## Risks and test signals
Dynamic proxy tracing can mishandle default methods or exception unwrapping. This test signals proxy dispatch correctness and span activation boundaries.
