# sources/object-store/rustfs/crates/s3select-query/src/instance.rs

## Purpose
This file assembles a RustFS S3 Select database instance from dispatcher, session, parser, function manager, optimizer, scheduler, execution factory, and table provider components.

## Important APIs, Types, And Functions
`RustFSms<D>` stores an `Arc<D: QueryDispatcher>` and implements `DatabaseManagerSystem`. `make_rustfsms` constructs fresh default components. `make_rustfsms_with_components` accepts shared cached components. Inline ignored tests demonstrate simple SQL and custom delimiter use against the global DB.

## Control Flow
The DBMS implementation delegates `execute`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan` to the dispatcher, wrapping outputs in `QueryHandle`. Construction builds `SessionCtxFactory`, `DefaultParser`, `CascadeOptimizer`, `LocalScheduler`, `SqlQueryExecutionFactory`, `BaseTableProvider`, then uses `SimpleQueryDispatcherBuilder` and `RustFSmsBuilder`.

## State And Persistence Behavior
Instances hold in-memory component Arcs. `make_rustfsms` creates new components; `make_rustfsms_with_components` reuses shared parser/function/execution/table-provider state. No durable state is stored.

## Dependencies And Integration Points
It connects the API `DatabaseManagerSystem` trait with the concrete query crate implementation. `lib.rs` calls `make_rustfsms_with_components` for cached global DB creation.

## Risks And Edge Cases
Builder `.expect("build db server")` can panic if the builder state is inconsistent, although required fields are set immediately before. The `is_test` flag controls whether sessions use in-memory fixtures or production `ECStore`. Ignored tests rely on fixture formatting and are not run by default.

## Test Signals
Integration tests cover database creation through both `make_rustfsms` and `get_global_db`, plus fresh DB creation. Inline tests are ignored but document expected CSV result shape and multi-byte delimiter behavior.
