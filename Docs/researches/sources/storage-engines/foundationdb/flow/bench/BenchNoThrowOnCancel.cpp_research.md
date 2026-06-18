# sources/storage-engines/foundationdb/flow/bench/BenchNoThrowOnCancel.cpp

Purpose: benchmarks coroutine cancellation with normal exception unwinding versus `NoThrowOnCancel` frame destruction.

Important APIs/types/functions: `CleanupCounter`, `cancelWithThrow`, `cancelWithoutThrow`, enums `CancelImpl` and `CancelScenario`, `makeCancelFuture`, `benchNoThrowOnCancelActor`, and wrapper `benchNoThrowOnCancel`.

Control flow: construct-and-cancel repeatedly creates one pending future on an unsent promise and cancels it. Batch-cancel pauses timing to build a vector of pending futures, resumes timing to cancel them, then pauses to assert cancellation results. The no-throw path uses a sentinel catch block that should not run.

State/persistence: local counters track RAII cleanup and caught cancellation exceptions. No persisted state.

Dependencies/integration: uses Flow futures, `NoThrowOnCancel`, cancellation error codes, `ThreadHelper.actor.h`, and Google Benchmark.

Risks: correctness assertions are embedded in benchmarks; changes to cancellation readiness/error representation can fail runs. Batch scenario times only cancellation, so construction costs are intentionally excluded.

Test signals: four registered benchmarks cover throwing/no-throw and construct/batch scenarios; cleanup count must equal cancellation count, and caught count distinguishes implementations.
