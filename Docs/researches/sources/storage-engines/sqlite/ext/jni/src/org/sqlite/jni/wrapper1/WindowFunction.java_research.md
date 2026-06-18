# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/WindowFunction.java

## Purpose
`WindowFunction.java` defines the Java-side abstract base for SQLite window UDFs in wrapper1. It extends aggregate UDF behavior with inverse and value callbacks needed by `sqlite3_create_window_function()` semantics.

## Important APIs, types, and functions
- `WindowFunction<T>` extends `AggregateFunction<T>`, inheriting aggregate state helpers and requiring aggregate step/final behavior.
- `xInverse(SqlFunction.Arguments args)` removes a row from the current window frame.
- `xValue(SqlFunction.Arguments args)` emits the current frame value without finalizing aggregate state.

## Control flow
The class itself has no implementation logic. `Sqlite.createFunction(..., WindowFunction f)` wraps instances in `SqlFunction.WindowAdapter`, and SQLite invokes `xStep`, `xInverse`, `xValue`, and `xFinal` through JNI callback flow.

## State and persistence behavior
Window state is managed by inherited aggregate state mechanisms in `AggregateFunction`; this file only defines the additional callback contract. Implementations decide the type and lifecycle of accumulated state.

## Dependencies and integration points
It depends on `AggregateFunction` and `SqlFunction.Arguments`. It integrates with `Sqlite.createFunction(String,int,int,WindowFunction)` and the native function adapter layer.

## Risks and edge cases
Implementations must keep `xInverse()` symmetric with `xStep()` or sliding-window results will drift. `xValue()` receives no SQL arguments but uses the context to set a result, so implementations should not assume ordinary argument data is present.

## Test signals
`Tester2.testUdfWindow()` registers a `winsumint` function and validates `xStep`, `xInverse`, `xValue`, and `xFinal` over a sliding `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` query.
