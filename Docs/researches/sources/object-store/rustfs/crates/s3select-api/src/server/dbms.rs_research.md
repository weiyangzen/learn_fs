# sources/object-store/rustfs/crates/s3select-api/src/server/dbms.rs

## Purpose
This file defines the database-manager API that external S3 Select handlers use to execute queries or drive the query pipeline in stages.

## Important APIs, Types, And Functions
`QueryHandle` stores the original `Query` and `Output`, with `new`, `query`, and consuming `result` accessors. `DatabaseManagerSystem` is an async trait exposing `execute`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan`.

## Control Flow
`execute` is the one-shot path. The other methods support staged execution where callers can create a state machine, inspect or transform the logical plan, then execute it.

## State And Persistence Behavior
`QueryHandle` owns an in-memory output stream; consuming `result` transfers stream ownership. No persistent query catalog or status store exists.

## Dependencies And Integration Points
The trait depends on API `Query`, `Output`, `QueryStateMachineRef`, and `Plan`. `RustFSms` implements it by delegating to `QueryDispatcher`.

## Risks And Edge Cases
Since `QueryHandle::result` consumes the handle, callers cannot read output twice. The trait does not define cancellation or query status despite the lower-level execution contract having `cancel`.

## Test Signals
Integration tests create global/fresh databases, call `execute`, and exercise staged state-machine/logical-plan/execute-plan calls.
