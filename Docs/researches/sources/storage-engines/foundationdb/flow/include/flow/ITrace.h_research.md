# sources/storage-engines/foundationdb/flow/include/flow/ITrace.h

## Purpose
`ITrace.h` defines interfaces for trace log writing, trace event formatting, and reporting trace-log health issues.

## Important APIs, Types, And Functions
It declares `ITraceLogWriter` with open/roll/close/write/sync and reference counting; `ITraceLogFormatter` with extension/header/footer/event formatting and reference counting; and `ITraceLogIssuesReporter` with issue add/resolve/retrieve and reference counting.

## Control Flow
Trace infrastructure calls writer lifecycle methods around trace files, formatter methods when starting/ending files and formatting events, and issue reporter methods when trace logging health changes.

## State And Persistence Behavior
State is implementation-owned. Writers persist trace bytes to files, network sinks, or memory; formatters are stateless or hold format settings; issue reporters maintain a set of active issues.

## Dependencies And Integration Points
It depends only on strings, sets, forward-declared `StringRef`, and `TraceEventFields`. Implementations integrate with Flow trace files, JSON/XML formatting, and operational diagnostics.

## Risks And Edge Cases
Implementations must be reference-counted consistently and handle writes during rolls/closes. `write(StringRef)` must not retain transient buffers unless copied. Issue retrieval should be synchronized in concurrent implementations.

## Test Signals
Writer lifecycle tests, formatter header/footer/event output, issue add/resolve idempotence, reference-count lifetime, roll during active logging, and sync error handling are useful.
