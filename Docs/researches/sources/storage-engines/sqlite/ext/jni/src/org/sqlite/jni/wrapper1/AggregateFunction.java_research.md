# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/AggregateFunction.java

## Purpose
`wrapper1.AggregateFunction<T>` is the higher-level wrapper1 abstraction for aggregate SQL functions, marked experimental/incomplete/untested.

## Important APIs, Types, and Functions
It implements `SqlFunction`, requires `xStep(SqlFunction.Arguments args)` and `xFinal(SqlFunction.Arguments args)`, and provides no-op `xDestroy()`. Nested `PerContextState<T>` maps `sqlite3_context.getAggregateContext()` keys to `ValueHolder<T>` values. Protected helpers `getAggregateState()` and `takeAggregateState()` expose that map to subclasses.

## Control Flow
Wrapper adapters in `SqlFunction` convert low-level JNI callbacks into `SqlFunction.Arguments`. Aggregate implementations fetch or initialize state during `xStep()` and remove/finalize it during `xFinal()`.

## State and Persistence Behavior
The per-function instance owns a `PerContextState` map. Each aggregate invocation in a statement gets a separate key; finalization removes it. Empty result sets can produce null state.

## Dependencies and Integration Points
It depends on wrapper1 `SqlFunction.Arguments`, wrapper1 `ValueHolder`, and low-level `sqlite3_context` aggregate keys via the arguments object.

## Risks
The map is unsynchronized and assumes callbacks for a given function instance do not run concurrently. Forgetting `takeAggregateState()` leaks per-context entries. Documentation contains stale `SQLFunction.PerContextState` references that should likely say `SqlFunction` or this class.

## Test Signals
Direct wrapper1 tests are not in this work item. Low-level `Tester1.testUdfAggregate()` covers the underlying aggregate-context behavior used by this helper.
