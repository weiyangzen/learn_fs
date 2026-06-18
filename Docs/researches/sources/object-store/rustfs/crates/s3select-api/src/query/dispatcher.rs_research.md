# sources/object-store/rustfs/crates/s3select-api/src/query/dispatcher.rs

## Purpose
This file defines the high-level query dispatcher contract. It separates database-manager callers from parsing, session creation, logical planning, and execution details.

## Important APIs, Types, And Functions
`QueryDispatcher` is an async trait with `execute_query`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan`. It passes `Query`, `QueryStateMachine`, `Plan`, and `Output` values across the API boundary.

## Control Flow
The intended flow is: build a state machine for the query and session, parse/build a logical plan, execute that plan, and return an `Output`. Implementors may expose the steps separately for callers that need staged execution.

## State And Persistence Behavior
The trait itself stores no state. Concrete dispatchers own reusable parser, factory, function metadata, and table-provider dependencies.

## Dependencies And Integration Points
It depends on the API crate's `Query`, `Output`, `QueryStateMachine`, and `Plan`. `SimpleQueryDispatcher` in `s3select-query` implements the full DataFusion-backed pipeline.

## Risks And Edge Cases
The trait has commented placeholders for query IDs, status, and cancellation, so lifecycle observability is incomplete at the interface level. Implementors must avoid recursive calls between trait and inherent methods with the same name.

## Test Signals
Integration tests exercise staged state-machine, logical-plan, and execute-plan calls through the `DatabaseManagerSystem` wrapper.
