# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.cc

## Purpose

This file implements the runtime mechanics for the operation pipeline DSL declared in `XrdClOperations.hh`. It handles response propagation, pipeline finalization, repeat/replace/stop/ignore control actions, and movement of final callbacks.

## Important APIs, Types, And Functions

Internal exception-like control structs are `StopPipeline`, `RepeatOpeation`, `ReplaceOperation`, `ReplacePipeline`, and `IgnoreError`. Implemented methods include `PipelineHandler` constructor, `AddOperation`, `HandleResponseImpl`, `HandleResponseWithHosts`, `HandleResponse`, `Assign`, `PreparePipelineStart`, and the static `Pipeline::Stop`, `Repeat`, `Replace`, and `Ignore` methods.

## Control Flow

When an operation completes, `PipelineHandler::HandleResponseImpl` takes ownership of `this`, copies the status, calls the user response handler if present, and catches control exceptions thrown by user code. Stop finalizes the promise with a supplied status. Repeat reruns the current operation with the same handler. Replace swaps in a new operation or pipeline. Ignore converts a failed status to OK and continues.

If no control action occurs, the handler deallocates payloads when there is no user handler, finalizes the promise on error or end-of-pipeline, or runs the next operation with the carried promise/final callback. `PreparePipelineStart` moves a final callback attached to the last handler to the first handler before execution starts.

## State And Persistence

Pipeline state is transient: current and next operations, response handler, timeout budget, promise, and final callback. No external persistence exists. Completion is persisted only into a `std::future` result or thrown exception path.

## Dependencies And Integration Points

It depends on `XrdClOperations.hh`, logging/default environment headers indirectly, `ResponseJob`, `JobManager`, and the operation handler wrappers. It is used by the pipeline operators and high-level APIs that return futures or wait synchronously.

## Risks

The typo `RepeatOpeation` is harmless internally but can confuse maintenance. Control flow relies on exceptions thrown from user callbacks, so catching broad exceptions in user code may break pipeline controls. `ReplacePipeline` runs the replacement without explicitly attaching `myself`, changing handler ownership flow. `HandleResponseImpl` copies the status before user callback because the callback may delete it; custom handlers must still follow ownership rules. Promise fulfillment must happen exactly once across all control paths.

## Test Signals

Pipeline tests should cover normal multi-operation success, failure stopping, final callback execution, stop with custom status, repeat current operation, replace current operation, replace whole pipeline, ignore error and continue, no-user-handler cleanup, host list propagation, and future value/exception behavior.
