# sources/distributed-fs/xrootd/src/XrdCl/XrdClParallelOperation.hh

## Purpose

This header implements the client pipeline combinator for running multiple `XrdCl::Pipeline` instances in parallel and collapsing their terminal statuses into one `Resp<void>` operation. It is part of the high-level operation DSL built on `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, `DefaultEnv`, `PostMaster`, and the client `JobManager`.

## Important APIs, Types, And Functions

`PolicyExecutor` is the abstract policy interface with `Examine(const XRootDStatus&)` and `Result()`. `ParallelOperation<HasHndl>` derives from `ConcreteOperation<ParallelOperation, HasHndl, Resp<void>>` and owns a vector of pipelines plus a selected policy. Public policy builders are `All()`, `Any()`, `Some(threshold)`, and `AtLeast(threshold)`. Free functions `Parallel(container)` and variadic `Parallel(operations...)` convert operations/pipelines into a vector.

The private policy implementations are `AllPolicy`, `AnyPolicy`, `SomePolicy`, and `AtLeastPolicy`. `Ctx` owns the final `PipelineHandler`, the policy, and a barrier that prevents an early completion callback from firing before `RunImpl` has launched all child pipelines. `PipelineEnd` is a `Job` used to schedule policy examination on the client worker pool.

## Control Flow

Construction move-copies child pipelines out of an input container and clears the source container. `RunImpl` installs `AllPolicy` by default, creates a shared `Ctx`, computes an effective timeout as the minimum of the inherited pipeline timeout and this operation's timeout, starts each non-null child pipeline with a completion lambda, then lifts the barrier. Each completion lambda queues `PipelineEnd`; the job calls `Ctx::Examine`; when the policy says the aggregate result is determined, `Ctx::Handle` atomically exchanges the handler pointer to `nullptr` and calls `HandleResponse(new XRootDStatus(...), nullptr)` exactly once.

## State And Persistence Behavior

State is transient in memory. The operation owns moved child pipelines and a policy until `RunImpl`, then transfers policy ownership into `Ctx`. `Ctx` is shared by completion jobs, so it remains alive until queued completions release it. The only persisted state is side effects of child pipelines elsewhere; this header itself writes no files and stores no global state.

## Dependencies And Integration Points

The file integrates the operation DSL with `DefaultEnv::GetPostMaster()->GetJobManager()`, so aggregate completion runs through the same worker pool as other client callbacks. It depends on `PipelineHandler`, `Pipeline`, `Operation<HasHndl>`, `ConcreteOperation`, `XRootDStatus`, and the client environment singleton. It is intended for asynchronous multi-target client workflows such as mirrored operations, replication, or quorum-style metadata/file operations.

## Risks And Edge Cases

Threshold validation is not explicit: `Some(0)`, `AtLeast(0)`, or thresholds larger than the pipeline count can produce unintuitive behavior. `SomePolicy::Examine` declares `std::unique_lock<std::mutex> resMtx;`, which does not lock the member mutex and shadows the member name; that is a concurrency risk for `failed`, `succeeded`, and `res`. Early-return policies do not cancel outstanding child pipelines, so late completions still enqueue jobs but cannot call the final handler after the atomic exchange. `barrier_t::wait` uses a single `if` instead of a predicate loop, so spurious wakeups would weaken the "all children started first" guarantee.

## Test Signals

Useful tests should cover all four policies with mixed success/failure orderings, empty and null child entries, threshold boundary values, callbacks completing before all child pipelines are launched, and repeated late completions after final handler delivery. Thread sanitizer or stress tests around `SomePolicy` would be valuable because its lock appears ineffective.
