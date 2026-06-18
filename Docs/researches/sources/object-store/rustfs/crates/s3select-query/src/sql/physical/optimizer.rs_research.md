# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/optimizer.rs

## Purpose
This file defines the local physical optimizer abstraction used after DataFusion physical planning.

## Important APIs, Types, And Functions
`PhysicalOptimizer` declares `optimize(plan, session) -> QueryResult<Arc<dyn ExecutionPlan>>` and `inject_optimizer_rule`, which accepts DataFusion `PhysicalOptimizerRule` instances.

## Control Flow
Concrete implementors receive a physical plan, optionally rewrite it with configured rules, and return the optimized plan. In the current stack, `DefaultPhysicalPlanner` implements this trait and returns the plan unchanged after DataFusion's session-level physical optimizer rules have already run during planning.

## State And Persistence Behavior
The trait has no persistence behavior. Implementations may hold in-memory rule lists.

## Dependencies And Integration Points
It is exported by `sql/physical/mod.rs` and consumed by `CascadeOptimizer` as the final physical-plan optimization stage.

## Risks And Edge Cases
The trait is separate from the API `PhysicalPlanner`, so implementors must keep planner-time DataFusion rules and post-planning optimization behavior synchronized. The default implementation currently performs no additional rewrite in `optimize`.

## Test Signals
No direct tests are local to this trait. `CascadeOptimizerBuilder` tests verify that a default physical optimizer component is installed, and integration tests cover the resulting execution plans.
