<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ThreadHelper.cpp -->
# sources/storage-engines/foundationdb/flow/ThreadHelper.cpp
- Purpose: Adds tests for safe conversion of thread futures into Flow futures and combines thread callbacks.
- Important APIs/types/functions: `ThreadCallback::addCallback`, helper functors `ThreadFutureSendObj` and `ThreadFutureCancelObj`, and tests `/flow/safeThreadFutureToFuture/Send` and `/flow/safeThreadFutureToFuture/Cancel`.
- Control flow: `addCallback` wraps two callbacks in `ThreadMultiCallback`. The send test starts a `std::thread` that sends a `ThreadSingleAssignmentVar`, awaits `safeThreadFutureToFuture`, then joins. The cancel test creates a never-completing main-thread future, cancels it from another thread, awaits the safe conversion, and expects `actor_cancelled`.
- State and persistence behavior: No persistent state. The tests allocate thread future objects and rely on join for cleanup.
- Dependencies and integration points: Depends on `ThreadHelper.actor.h`, Flow coroutines/futures, `onMainThread`, `UnitTest`, `g_network`, and `std::thread`.
- Risks: Tests are skipped in simulation because `std::thread` is unsupported there. The value of the file is race detection under TSAN; using the unsafe conversion should produce a data race.
- Test signals: TSAN-enabled runs of the two tests verify send and cancellation safety across threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ThreadHelper.cpp -->
