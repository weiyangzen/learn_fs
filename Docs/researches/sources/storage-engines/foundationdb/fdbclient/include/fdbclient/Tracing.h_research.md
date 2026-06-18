<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h

## Purpose
`Tracing.h` declares the client/server span model used for FoundationDB tracing. It provides span contexts, span events, span attributes, trace sampling flags, span kind/status enums, and the tracer interface.

## Important APIs, Types, and Functions
Important exports include `Location`, the `_loc` literal, `TraceFlags`, `SpanContext`, `SpanKind`, `SpanStatus`, `SpanEventRef`, `Span`, `TracerType`, `ITracer`, and `openTracer`. `Span` supports construction from a context or parent, move-only ownership, links, events, attributes, parent replacement, and destructor-driven tracing behavior.

## Control Flow
Callers create spans at RPC or operation boundaries, passing parent context when available. Constructors copy trace IDs and sampling flags from parents, assign random span IDs, record begin time from `g_network`, and add local address attributes. Links can force sampling and initialize an otherwise invalid context. The destructor or assignment implementation emits the span to the active tracer when appropriate.

## State and Persistence Behavior
Trace data is in-memory until passed to an `ITracer`. `Span` owns strings, attributes, links, and events in an arena. Serialized `SpanContext` values propagate through RPC requests such as storage reads. The header itself has no durable persistence, but log-file tracers can persist emitted spans externally.

## Dependencies and Integration Points
It depends on Flow network, randomness, arenas, transport address reporting, and FDB key/value types. Storage read requests include `SpanContext`, and NativeAPI, proxies, commit paths, and server actors use spans for OpenTelemetry-like trace propagation.

## Risks and Edge Cases
`Span(Location)` intentionally creates mostly unsampled background spans, so instrumentation can appear absent unless parent sampling is present. Constructors warn that one overload does not enforce parent/context trace ID equality. Destruction-time emission requires move semantics to invalidate moved-from spans correctly. `TracerType` names are intentionally not stable client API.

## Test Signals
Signals include trace serialization tests, simulation tracer tests for `NETWORK_LOSSY` and `SIM_END`, log tracer output checks, parent/child propagation tests, sampling flag tests, and RPC request tests that preserve `SpanContext`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h -->
