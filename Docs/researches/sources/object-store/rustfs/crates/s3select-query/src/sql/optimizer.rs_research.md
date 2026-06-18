# sources/object-store/rustfs/crates/s3select-query/src/sql/optimizer.rs

## Purpose
This file implements the cascade optimizer that turns a logical query plan into a physical execution plan by composing analysis, logical optimization, and physical planning.

## Important APIs, Types, And Functions
`CascadeOptimizer` stores an analyzer, logical optimizer, and physical planner. It implements API `Optimizer`. `CascadeOptimizerBuilder` constructs the default stack from `DefaultAnalyzer`, `DefaultLogicalOptimizer`, and `DefaultPhysicalPlanner`.

## Control Flow
`optimize` logs the input logical plan, runs analysis, wraps the analyzed plan back into `QueryPlan`, runs logical optimization, then calls the physical planner. Explain/analyze plans are detected to avoid inappropriate optimizer behavior where needed by the implementation.

## State And Persistence Behavior
The optimizer stack is shared in memory and produces plans only. It writes no durable state.

## Dependencies And Integration Points
It integrates API optimizer contracts with local analyzer, logical optimizer, and physical planner implementations. `SqlQueryExecutionFactory` receives it from `instance` or the global cache.

## Risks And Edge Cases
DataFusion optimizer/planner errors propagate to query execution. Explain/analyze handling must remain aligned with DataFusion logical-plan variants. Debug logging can expose query plans and schemas.

## Test Signals
End-to-end CSV, JSON, parquet, filter, aggregation, order, limit, invalid SQL, and invalid function tests exercise this optimizer path.
