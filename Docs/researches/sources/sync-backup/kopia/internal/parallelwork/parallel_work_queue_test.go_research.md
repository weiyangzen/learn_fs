# sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue_test.go

Purpose: tests queue ordering, concurrency completion, error propagation, progress reporting, and completion wrappers.

Important APIs/types/functions: `TestEnqueueFrontAndProcess`, `TestEnqueueBackAndProcess`, `TestProcessWithError`, `TestWaitForActiveWorkers`, `TestProgressCallback`, and `TestOnNthCompletion`.

Control flow: creates queues, enqueues callbacks that send results, block, or return errors, then runs `Process` with multiple workers and asserts counters/order/returned errors.

State and persistence behavior: uses channels and atomics for deterministic in-memory synchronization.

Dependencies and integration points: exercises the public `parallelwork` API from an external test package.

Risks and test signals: good coverage for core scheduling; race-detector runs are important because cond-variable bugs may pass normal tests.
