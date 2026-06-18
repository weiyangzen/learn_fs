# sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/local.rs

## Purpose
This file implements the local in-process scheduler for DataFusion execution plans.

## Important APIs, Types, And Functions
`LocalScheduler` implements API `Scheduler`. `schedule(plan, context)` calls DataFusion `execute_stream` and wraps the resulting stream in `ExecutionResults`.

## Control Flow
There is a single path: DataFusion executes the physical plan with the provided task context, and the stream is returned to the query execution layer.

## State And Persistence Behavior
The scheduler is stateless. Execution state lives in DataFusion's stream and task context.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, `TaskContext`, and `execute_stream`, plus API scheduler types. It is constructed in `instance` and the global component cache.

## Risks And Edge Cases
There is no admission control, parallelism tuning, distributed execution, or cancellation wrapper here. Errors from `execute_stream` propagate as DataFusion errors.

## Test Signals
All successful integration tests use this scheduler.
