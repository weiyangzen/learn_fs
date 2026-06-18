# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AggregateFunction.java

## Purpose
Base class for Java aggregate SQL functions registered through `sqlite3_create_function`.

## Important APIs, Types, And Functions
Defines abstract `xStep(sqlite3_context, sqlite3_value[])` and `xFinal(sqlite3_context)`, optional `xDestroy()`, and nested `PerContextState<T>`. Protected helpers `getAggregateState()` and `takeAggregateState()` manage per-aggregate accumulator state.

## Control Flow
SQLite calls `xStep()` for each row, then `xFinal()` once per aggregate invocation. `getAggregateState()` uses `sqlite3_context.getAggregateContext(true)` to map a C aggregate context key to a Java `ValueHolder<T>`. `takeAggregateState()` removes the mapping at finalization.

## State And Persistence Behavior
State is transient Java heap state stored in a `HashMap<Long, ValueHolder<T>>`. The key comes from native aggregate context allocation. Callers must remove state in `xFinal()` to avoid retaining per-statement state.

## Dependencies And Integration Points
Depends on `SQLFunction`, `sqlite3_context`, `sqlite3_value`, and `ValueHolder`. The JNI layer recognizes the callback method names/signatures when installing UDFs.

## Risks And Edge Cases
If a query has no result rows, `xFinal()` may see no existing state. Exceptions in `xStep()` are suppressed with possible debug output; exceptions in `xFinal()` are converted to result errors. Missing `takeAggregateState()` leaks Java state until the function object is discarded.

## Test Signals
Register aggregate UDFs over grouped and empty inputs, multiple invocations in one `SELECT`, exception paths, and `xDestroy()` cleanup.
