# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneProtocolMessageDispatcher.java

## Purpose

`OzoneProtocolMessageDispatcher` is a generic server-side RPC helper that wraps request handling with trace span import/creation, request/response logging, and protocol message metrics.

## Important APIs, Types, and Functions

The class is generic over request, response, and enum request type. Constructors accept service name, `ProtocolMessageMetrics`, logger, and optional request/response preprocessors. `processRequest` takes a request, checked method call, type, and trace ID. `escapeNewLines` is the default log preprocessor.

## Control Flow

`processRequest` imports a trace span, enters scope, logs the request at trace or debug level, measures the method call with `protocolMessageMetrics.measure(type)`, logs the response at trace level, returns the response, and always ends the span in `finally`.

## State and Persistence Behavior

It holds immutable logging/metrics/preprocessor dependencies. No persistence.

## Dependencies and Integration Points

It integrates server-side translators with OpenTelemetry `Span`/`Scope`, `TracingUtil`, `ProtocolMessageMetrics`, Ratis `CheckedFunction`, and protobuf `ServiceException`.

## Risks and Edge Cases

Default preprocessing calls `toString()` and regex replacement, which can be expensive or leak sensitive data at trace level. If a preprocessor throws, request handling fails before the method call. Metrics measurement depends on `measure(type)` returning a closeable even for exceptions.

## Test Signals

Test successful request flow, method exception propagation, span end on exception, metrics close on exception, trace/debug logging branches with custom preprocessors, and newline escaping.
