# sources/object-store/rustfs/crates/s3select-api/src/query/physical_planner.rs

## Purpose
This file defines a physical planner abstraction for converting a DataFusion logical plan to a DataFusion physical execution plan.

## Important APIs, Types, And Functions
`PhysicalPlannerRef` is an `Arc<dyn PhysicalPlanner + Send + Sync>`. `PhysicalPlanner::create_physical_plan(&LogicalPlan, &SessionCtx) -> QueryResult<Arc<dyn ExecutionPlan>>` is async, and `inject_physical_transform_rule` lets implementations add DataFusion extension planners.

## Control Flow
The default optimizer stack uses its own physical planner implementation to build the final DataFusion execution plan before scheduling.

## State And Persistence Behavior
This is a stateless interface; implementations produce in-memory execution plans.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, API `Plan`, and `SessionCtx`. It is implemented by `DefaultPhysicalPlanner` in the query crate.

## Risks And Edge Cases
The abstraction works below the API `Plan` layer: callers must extract or produce a DataFusion `LogicalPlan` before invoking it. Future custom logical extension nodes require matching physical extension planners.

## Test Signals
No local tests. End-to-end query execution verifies physical planning indirectly.
