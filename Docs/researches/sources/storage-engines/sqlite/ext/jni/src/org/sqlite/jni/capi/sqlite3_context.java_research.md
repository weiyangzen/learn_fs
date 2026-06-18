# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_context.java

## Purpose
`sqlite3_context` wraps SQLite UDF callback context handles and provides a Java-friendly aggregate-context key.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_context>` and adds synchronized `Long getAggregateContext(boolean initIfNeeded)`. This calls `CApi.sqlite3_aggregate_context()` and caches a stable key for a matching set of aggregate/window callbacks.

## Control Flow
Scalar, aggregate, and window callbacks receive a context. Aggregate/window functions call `getAggregateContext(true)` from step/value/inverse paths and `getAggregateContext(false)` from final paths.

## State and Persistence Behavior
The `aggregateContext` field caches the native key. Numeric zero is treated as null in public return semantics. A no-row aggregate finalization can legally return null because no state was initialized.

## Dependencies and Integration Points
It integrates with low-level `AggregateFunction`, `WindowFunction`, wrapper1 aggregate helpers, and `CApi.sqlite3_aggregate_context()`.

## Risks
The returned key is valid only within a single SQL statement execution and must not be reused across statements. Retaining the `sqlite3_context` object after a callback is illegal; tests verify native pointer invalidation.

## Test Signals
`Tester1.testUdfAggregate()` and `testUdfWindow()` validate distinct aggregate contexts for multiple invocations, state reset after statement reset/finalize, and null final state for empty result sets.
