# sources/storage-engines/rocksdb/monitoring/instrumented_mutex.cc

Purpose: Implements mutex and condition-variable wrappers that record perf-context and statistics timing for DB mutex waits and condition waits.

Important APIs/types/functions: `stats_for_report` enables statistics reporting only when a clock and statistics object exist and the stats level includes mutex timing. `InstrumentedMutex::Lock` wraps `LockInternal` with `PERF_CONDITIONAL_TIMER_FOR_MUTEX_GUARD`. `InstrumentedCondVar::Wait` and `TimedWait` do the same for condition waits.

Control flow: Lock/wait methods create a scoped `PerfStepTimer`, optionally start it when the stats code is `DB_MUTEX_WAIT_MICROS`, call internal wait/lock functions, and stop on scope exit. Debug builds call `ThreadStatusUtil::TEST_StateDelay` before blocking. `TimedWaitInternal` exposes a sync-point callback to alter absolute wait time for tests.

State/dependencies: Uses the wrapped `port::Mutex`/`port::CondVar`, optional `Statistics`, optional `SystemClock`, and stats code. Depends on perf-context macros, thread-status debug hooks, `SystemClock`, and sync points.

Risks/test signals: Instrumentation is gated by compile-time perf flags and runtime stats level. `COERCE_CONTEXT_SWITCH` can deliberately yield/sleep around DB mutex waits for stress. Timing overhead is minimized but still present when enabled.
