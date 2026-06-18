# sources/object-store/rustfs/crates/obs/src/telemetry/guard.rs

## Purpose
Defines `OtelGuard`, the RAII owner for observability runtime resources, and implements ordered shutdown for tracing, metrics, logging, profiling, cleanup tasks, and non-blocking log writers.

## Important APIs, Types, and Functions
Type aliases `ProfilingAgent` and `MemoryProfilingAgent` are feature/platform gated. `format_guard_shutdown_stderr_message()` builds fallback diagnostics. `OtelGuard` stores optional `SdkTracerProvider`, `SdkMeterProvider`, `SdkLoggerProvider`, profiling agents, cleanup task handle, file tracing worker guard, and stdout worker guard. `Debug` reports only presence flags.

## Control Flow
`Drop` shuts resources down in a deliberate order: tracer provider, meter provider, profiling agents, cleanup task abort, logger provider, file tracing guard, and stdout guard. Provider shutdown failures are logged through tracing when a dispatcher exists, or printed to stderr otherwise. Logger provider failures always go to stderr after logger shutdown becomes unreliable.

## State and Persistence
The guard owns runtime handles but does not persist state. Dropping worker guards flushes buffered logs. Aborting the cleanup task stops future log cleanup passes.

## Dependencies and Integration Points
Constructed by telemetry initialization paths such as local logging and OTLP setup. Depends on OpenTelemetry SDK providers, tracing appender worker guards, optional Pyroscope, and Tokio task handles.

## Risks
Drop-time operations must remain non-panicking. Shutdown logging depends on dispatcher availability and resource order. Aborting cleanup means in-flight cleanup work may stop abruptly, which is acceptable for shutdown but should not be used for normal rotation control.

## Test Signals
Unit test verifies the stderr fallback shutdown message is actionable and includes resource/error data. More integration coverage would require fake providers or feature-gated profiling paths.
