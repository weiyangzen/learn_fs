# sources/object-store/rustfs/crates/s3select-api/src/query/optimizer.rs

## Purpose
This file defines the optimizer abstraction that converts a logical `QueryPlan` into a DataFusion physical `ExecutionPlan`.

## Important APIs, Types, And Functions
`OptimizerRef` is an `Arc<dyn Optimizer + Send + Sync>`. `Optimizer::optimize(&QueryPlan, &SessionCtx) -> QueryResult<Arc<dyn ExecutionPlan>>` is async and returns the physical plan to schedule.

## Control Flow
`SqlQueryExecution` calls this trait during its optimize phase, then passes the returned physical plan to a scheduler.

## State And Persistence Behavior
The trait is stateless. Concrete optimizers may hold analyzer, logical optimizer, and physical planner components but produce in-memory plans only.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, API `QueryPlan`, and `SessionCtx`. `CascadeOptimizer` is the default implementation.

## Risks And Edge Cases
Since optimization is the boundary where logical plans become physical plans, errors include both logical optimizer and physical planner failures. Implementations must respect the `is_explain` path.

## Test Signals
Integration tests indirectly cover this path through normal query execution and explain/invalid-query behavior.
