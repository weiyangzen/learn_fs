# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/WindowFunction.java

## Purpose
`WindowFunction<T>` is the low-level JNI UDF abstraction for SQLite window functions.

## Important APIs, Types, and Functions
It extends `AggregateFunction<T>` and adds abstract `xInverse(sqlite3_context cx, sqlite3_value[] args)` and `xValue(sqlite3_context cx)`, matching `sqlite3_create_window_function()` callbacks. Inherited aggregate methods provide `xStep()`, `xFinal()`, and per-context state helpers.

## Control Flow
SQLite invokes `xStep()` as rows enter a frame, `xInverse()` as rows leave, `xValue()` for the current frame result, and `xFinal()` at the end. The JNI registration layer dispatches native calls into this object.

## State and Persistence Behavior
State is inherited from `AggregateFunction`, usually keyed by `sqlite3_context.getAggregateContext()`. Implementations must clear state in `xFinal()` and be prepared for null state.

## Dependencies and Integration Points
It depends on `AggregateFunction`, `sqlite3_context`, `sqlite3_value`, and registration through `CApi.sqlite3_create_function()` or related wrapper logic.

## Risks
The comments warn exceptions in `xInverse()` or `xValue()` may not propagate normally and may only appear through diagnostics. Incorrect state cleanup can cross-contaminate repeated statement execution.

## Test Signals
`Tester1.testUdfWindow()` implements a rolling integer sum and validates expected SQLite window-function example results for five rows.
