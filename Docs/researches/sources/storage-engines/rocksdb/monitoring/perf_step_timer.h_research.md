# sources/storage-engines/rocksdb/monitoring/perf_step_timer.h

Purpose: Provides the scoped timer primitive used by perf-context and IO-stats macros to accumulate elapsed wall or CPU time and optionally report tickers to `Statistics`.

Important APIs/types/functions: `PerfStepTimer` constructor captures metric pointer, optional clock, CPU-time flag, required `PerfLevel`, optional statistics object, and ticker type. Public methods are `Start`, `Measure`, and `Stop`; destructor calls `Stop`.

Control flow: The constructor precomputes whether perf counters are enabled and only resolves a clock when either perf or statistics reporting is needed. `Start` stores current time. `Measure` adds elapsed duration to the metric and resets the start time. `Stop` adds elapsed duration to the metric when enabled and calls `RecordTick` on optional statistics.

State and dependencies: Stores booleans, ticker type, clock pointer, start timestamp, metric pointer, and statistics pointer. Depends on `perf_level_imp.h`, `statistics_impl.h`, and `rocksdb/system_clock.h`.

Risks/test signals: `metric_` must remain valid for the timer lifetime. Statistics reporting can run even when perf-level recording is disabled. Destructor-based stop makes the macro guards exception-safe in C++ terms, but double-stop is avoided only through `start_ = 0`.
