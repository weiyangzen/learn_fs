# sources/object-store/rustfs/crates/s3select-query/src/sql/planner.rs

## Purpose
This file implements the generic SQL-to-logical-plan adapter over DataFusion's `SqlToRel`.

## Important APIs, Types, And Functions
`SqlPlanner<'a, S: ContextProviderExtension>` stores a schema/context provider. Its `LogicalPlanner` implementation accepts `ExtStatement` and returns API `Plan`. The implementation uses async recursion to resolve SQL statements through DataFusion and wrap the resulting logical plan in `QueryPlan`.

## Control Flow
When passed an `ExtStatement::SqlStatement`, the planner calls DataFusion's SQL-to-rel planner with the metadata provider. It rejects unsupported statements through DataFusion/planner errors and marks the resulting plan as a query with `is_tag_scan: false`.

## State And Persistence Behavior
The planner borrows metadata context for the lifetime of planning and persists nothing.

## Dependencies And Integration Points
It depends on DataFusion `SqlToRel`, sqlparser statements, API `LogicalPlanner`, `Plan`, `QueryPlan`, and the metadata `ContextProviderExtension`. `DefaultLogicalPlanner` wraps this type.

## Risks And Edge Cases
Only SQL statements supported by DataFusion and the metadata provider can be planned. `is_tag_scan` is always false, so any future tag-scan detection must be added here.

## Test Signals
Planner behavior is covered by integration tests for select, where, group by, order by, limit, invalid columns, unsupported DML/DDL, and multi-format object scans.
