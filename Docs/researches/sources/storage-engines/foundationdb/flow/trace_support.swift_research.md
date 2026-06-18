# sources/storage-engines/foundationdb/flow/trace_support.swift

Purpose: This Swift wrapper provides a fluent API around C++ `Flow.TraceEvent` for Swift code. It lets callers write chained `.detail(...)` calls without relying on mutating Swift value semantics for a C++ type that mutates internally.

Important APIs and types: `STraceEvent` is a `final class` with `event: Flow.TraceEvent`, static `make(_:_:)`, and overloads of `detail` for `OptionalStdString`, `std.string`, `Float`, `Double`, `Int`, `OptionalInt64`, `UInt32`, `Int32`, `Int64`, and `UInt64`. The private `keepAlive: [std.string]` stores copied detail names and event types.

Control flow: Initialization copies the event type into `keepAlive` and constructs the C++ trace event from its unsafe C string plus `Flow.UID`. Each detail overload appends the detail key to `keepAlive`, calls the concrete C++ `addDetail` template overload, and returns `self` for chaining.

State and persistence behavior: There is no persistent state; the important runtime state is ownership of `std.string` values whose C pointers are passed into C++ code. The wrapper's lifetime must cover the trace-event mutation path so detail names remain valid.

Dependencies and integration points: It imports `Flow` and bridges Swift code to C++ tracing. The overload list works around Swift/C++ interop limitations around generic template expansion; unsupported mappings such as `Int8` are left commented out.

Risks: Lifetime bugs are possible if `Flow.TraceEvent` stores pointers longer than the wrapper's `keepAlive`. Type coverage must be expanded manually for new detail types. Tests should emit trace events from Swift, verify details appear with correct values, exercise optional values, and check that chaining and discardable `make` usage both compile and run.
