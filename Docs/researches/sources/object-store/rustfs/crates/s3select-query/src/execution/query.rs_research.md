# sources/object-store/rustfs/crates/s3select-query/src/execution/query.rs

## Purpose
This file implements SQL query execution: optimize a logical query plan, schedule the resulting physical plan, and expose the DataFusion record-batch stream.

## Important APIs, Types, And Functions
`SqlQueryExecution` stores the state machine, `QueryPlan`, optimizer, scheduler, and an optional `AbortHandle`. Its inherent `start` performs optimization and scheduling. The `QueryExecution` trait implementation wraps that future in `futures::future::abortable` and exposes `cancel`.

## Control Flow
Execution starts by timing and marking the optimize phase, calls `optimizer.optimize`, then times and marks the schedule phase, calls `scheduler.schedule`, and returns `Output::StreamData`. The trait `start` stores the abort handle before awaiting. `cancel` marks the state machine cancelled and aborts the stored future if present.

## State And Persistence Behavior
Cancellation state is held in a `parking_lot::Mutex<Option<AbortHandle>>`; query phase state is in `QueryStateMachine`. No durable state is written.

## Dependencies And Integration Points
It connects API `QueryExecution`, `Optimizer`, `Scheduler`, `Output`, and `QueryStateMachine` with the concrete query crate optimizer and scheduler.

## Risks And Edge Cases
The abort handle only cancels the future up to stream creation; after `start` returns a stream, later stream polling is not tied to this handle. `finish` and `fail` are not called on success or error. Cloning the physical plan before scheduling may be unnecessary but harmless with `Arc`.

## Test Signals
Integration tests exercise normal execution, concurrent starts, and staged execution. There are no focused cancellation tests.
