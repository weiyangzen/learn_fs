# sources/object-store/rustfs/crates/s3select-api/src/query/logical_planner.rs

## Purpose
This file defines logical plan types and the planner trait used to convert parsed statements into executable query plans.

## Important APIs, Types, And Functions
`Plan::Query(QueryPlan)` is the only plan kind. `Plan::schema` exposes the Arrow schema for the underlying DataFusion plan. `QueryPlan` stores `df_plan: DFPlan` and `is_tag_scan`. `QueryPlan::is_explain` detects DataFusion `Explain` and `Analyze` logical plans. `LogicalPlanner::create_logical_plan` is the async planner interface.

## Control Flow
Dispatchers call the planner after parsing. The planner returns a `Plan`, which the execution factory turns into a query execution.

## State And Persistence Behavior
Plans are immutable in-memory values. `is_tag_scan` is metadata for later stages; no persistence happens here.

## Dependencies And Integration Points
It depends on DataFusion logical plan and Arrow schema types, the API `ExtStatement`, and `SessionCtx`. `DefaultLogicalPlanner` in `s3select-query` implements the trait through the generic SQL planner.

## Risks And Edge Cases
The enum currently only supports query plans, so future DDL/control commands require new variants. `Plan::schema` clones the DataFusion schema into a new `Arc`, which is safe but assumes every plan has a valid schema.

## Test Signals
Integration tests build logical plans from state machines and execute them when present.
