# sources/object-store/rustfs/crates/s3select-api/src/query/analyzer.rs

## Purpose
This file defines the analyzer abstraction used between logical planning and optimization. It lets implementation crates run DataFusion logical-analysis rules without coupling callers to a concrete analyzer.

## Important APIs, Types, And Functions
`AnalyzerRef` is an `Arc<dyn Analyzer + Send + Sync>`. `Analyzer::analyze(&LogicalPlan, &SessionCtx) -> QueryResult<LogicalPlan>` accepts an immutable DataFusion logical plan and session wrapper and returns an analyzed logical plan.

## Control Flow
There is no local execution logic. Implementors receive the logical plan created by the planner, run their chosen analysis rules, and return a new plan for optimization or execution.

## State And Persistence Behavior
The trait is stateless. State is carried by the concrete implementation and the `SessionCtx`; no persistence or global mutation occurs here.

## Dependencies And Integration Points
The contract depends on DataFusion `LogicalPlan`, the API crate `SessionCtx`, and the crate-wide `QueryResult`. `rustfs-s3select-query/src/sql/analyzer.rs` provides the default implementation backed by DataFusion's analyzer.

## Risks And Edge Cases
Because the trait returns a full logical plan, implementations must preserve schema and table-provider semantics. Analyzer failures propagate as `QueryError` through `QueryResult`.

## Test Signals
No tests are local to this interface file. Coverage comes from the default analyzer and end-to-end query tests.
