# sources/object-store/rustfs/crates/s3select-api/src/query/scheduler.rs

## Purpose
This file defines the scheduling contract for running a DataFusion physical plan and returning a record-batch stream.

## Important APIs, Types, And Functions
`SchedulerRef` is an `Arc<dyn Scheduler + Send + Sync>`. `Scheduler::schedule(plan, task_context)` returns `ExecutionResults`. `ExecutionResults` wraps `SendableRecordBatchStream` and exposes it through `stream(self)`.

## Control Flow
`SqlQueryExecution` calls the scheduler after optimization, passing the plan and the session task context. The local scheduler delegates to DataFusion's `execute_stream`.

## State And Persistence Behavior
The scheduler interface is stateless; actual runtime state is in DataFusion's task context and stream.

## Dependencies And Integration Points
It depends on DataFusion `TaskContext`, `ExecutionPlan`, `SendableRecordBatchStream`, and DataFusion error results. `LocalScheduler` implements it for single-process execution.

## Risks And Edge Cases
Schedulers must manage stream ownership and cancellation carefully. This abstraction does not expose queueing, resource admission, or distributed scheduling metadata.

## Test Signals
Integration tests exercise scheduling through real query execution and concurrent query cases.
