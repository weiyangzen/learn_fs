# sources/storage-engines/foundationdb/flow/swift_concurrency_hooks.cpp

## Purpose
This C++ file implements Flow hooks used by the Swift concurrency runtime integration. It exposes small wrappers around the Flow network clock/delay APIs and provides an enqueue hook that routes Swift jobs into FoundationDB's network scheduler.

## Important APIs, Types, And Functions
`SwiftJobTask` is a `N2::Task`/`FastAllocated` wrapper around a `swift::Job*` that runs the job on the generic executor and deletes itself, though the active enqueue hook currently bypasses it. Exported hook functions are `flow_gNetwork_now`, `flow_gNetwork_delay(double seconds, TaskPriority taskID)`, `net2_enqueueGlobal_hook_impl(swift::Job*, swiftcall function pointer)`, and `swift_job_run_generic`.

## Control Flow
`flow_gNetwork_now` returns `g_network->now()`. `flow_gNetwork_delay` returns `g_network->delay(seconds, taskID)`. The Net2 enqueue hook asserts a live `g_network` and delegates the Swift job to `net->_swiftEnqueue(job)`. Commented code shows a prior or planned path that would map Swift priority to Net2 priority and wrap the job in an ordered task. `swift_job_run_generic` calls `swift_job_run(job, ExecutorRef::generic())` only when `WITH_SWIFT` is defined.

## State And Persistence
The file owns no persistent state. It uses the global Flow network pointer and transient Swift job pointers supplied by the Swift runtime. If `SwiftJobTask` is used in the future, each task self-deletes after running.

## Dependencies And Integration Points
Dependencies include `flow/swift_concurrency_hooks.h`, `flow/swift.h`, Swift ABI `Task.h`, `TLSConfig.h`, Net2 task types, `FastAllocated`, `Future<Void>`, `TaskPriority`, and `g_network`. It integrates Swift global job enqueueing with FoundationDB's single-threaded/event-loop scheduling model.

## Risks
The hook assumes `g_network` is initialized before Swift jobs are enqueued. The `swiftcall` function pointer parameter is unused, so changes in Swift runtime hook expectations could require updates. Priority mapping is currently not applied in this hook, which can affect fairness or latency for Swift tasks. Direct use of Swift ABI headers and external `swift_job_run` makes the file sensitive to Swift ABI changes and build flags.

## Test Signals
Integration tests should verify Swift async jobs enqueued from Swift run on the Flow network, `flow_gNetwork_delay` resumes after the expected simulated/real delay, and builds without `WITH_SWIFT` do not call unavailable Swift runtime symbols. Scheduler tests should watch ordering/fairness if priority mapping is restored.
