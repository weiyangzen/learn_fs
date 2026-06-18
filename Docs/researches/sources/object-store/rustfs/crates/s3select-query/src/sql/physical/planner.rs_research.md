# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/planner.rs

## Purpose
This file implements the default physical planner that converts logical query plans to DataFusion execution plans.

## Important APIs, Types, And Functions
`DefaultPhysicalPlanner` wraps DataFusion physical planning facilities. Its API `PhysicalPlanner` implementation accepts a DataFusion `LogicalPlan` and creates an `Arc<dyn ExecutionPlan>` using a session state augmented with physical optimizer rules.

## Control Flow
The planner is called after analysis/logical optimization. It delegates physical-plan creation to DataFusion with the query session, preserving explain/analyze behavior through the logical plan supplied by earlier stages.

## State And Persistence Behavior
The planner is stateless and produces in-memory execution plans.

## Dependencies And Integration Points
It depends on API `PhysicalPlanner`, `Plan`, `SessionCtx`, and DataFusion physical planner APIs. `CascadeOptimizer` uses it as the final step.

## Risks And Edge Cases
Physical planning is version-sensitive to DataFusion APIs and to custom table providers. Errors here usually indicate unsupported logical plans, missing table metadata, or object-store/table-source mismatches.

## Test Signals
All successful query integration tests exercise this planner.
