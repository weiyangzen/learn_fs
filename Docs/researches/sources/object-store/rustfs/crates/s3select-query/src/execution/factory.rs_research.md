# sources/object-store/rustfs/crates/s3select-query/src/execution/factory.rs

## Purpose
This file implements the execution factory that turns API logical plans into concrete SQL query executions.

## Important APIs, Types, And Functions
`QueryExecutionFactoryRef` is an `Arc<dyn QueryExecutionFactory + Send + Sync>`. `SqlQueryExecutionFactory` stores an optimizer and scheduler. `new` constructs it, and the `QueryExecutionFactory` implementation returns `SqlQueryExecution` for `Plan::Query`.

## Control Flow
The dispatcher asks the factory to create an execution after logical planning. The factory pattern-matches the plan enum and injects the shared optimizer and scheduler.

## State And Persistence Behavior
The factory is immutable and shares `Arc` dependencies. It does not persist state.

## Dependencies And Integration Points
It depends on API execution/planner/optimizer/scheduler traits and the local `SqlQueryExecution`.

## Risks And Edge Cases
Only `Plan::Query` is supported. New plan variants require updating this factory or they will be unhandled at compile time.

## Test Signals
Covered indirectly by all successful query execution tests.
