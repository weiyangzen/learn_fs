# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TraceV2Callback.java

## Purpose
`TraceV2Callback` models the callback accepted by `sqlite3_trace_v2()` in Java.

## Important APIs, Types, and Functions
It extends `CallbackProxy` and exposes `int call(int traceFlag, Object pNative, @Nullable Object pX)`. The native callback's user-data argument is elided because Java objects can keep instance-local state.

## Control Flow
After registration, SQLite invokes `call()` for trace events. `pNative` is a `sqlite3_stmt` for statement/profile/row events and a `sqlite3` for close events. `pX` is a SQL string for `SQLITE_TRACE_STMT`, a `Long` nanosecond estimate for `SQLITE_TRACE_PROFILE`, and null for row/close events.

## State and Persistence Behavior
The interface stores no state. Implementations commonly close over counters or logging targets. Event wrapper objects are transient native views and should not be retained beyond the callback.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_trace_v2`, `CallbackProxy`, `sqlite3`, `sqlite3_stmt`, and nullable annotations.

## Risks
Incorrect casts based on `traceFlag` will fail at runtime. Throwing is allowed by the binding contract but is converted to C-level error information rather than normal Java propagation.

## Test Signals
`Tester1.testTrace()` registers all trace flags, validates event object types, checks non-BMP SQL survives Java/native round trips, counts statement/profile/row events, and confirms close tracing fires when the DB is closed.
