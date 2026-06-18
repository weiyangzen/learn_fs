# sources/storage-engines/rocksdb/test_util/mock_time_env.h

Purpose: defines `MockSystemClock`, a test `SystemClockWrapper` that advances logical time without sleeping. The file notes that `SpecialEnv` is preferred for DB tests because it adds DB-safe mock-time hooks.

Important APIs: `GetCurrentTime()`, `NowSeconds()`, `NowMicros()`, and `NowNanos()` read `current_time_us_`. `SetCurrentTime()`, `SleepForMicroseconds()`, and `MockSleepForSeconds()` advance time monotonically with overflow assertions. `RealNowMicros()` delegates to the wrapped clock. `TimedWait()` synthetically unlocks the condition-variable mutex, yields, randomly chooses timeout vs wakeup, and if timing out advances mock time to the deadline.

State behavior: `current_time_us_` is atomic, but comments state fake sleep is not thread-safe as a test-time abstraction. `TimedWait()` temporarily releases and reacquires the caller's mutex, and emits sync points around the synthetic sleep.

Dependencies/integration: uses RocksDB `SystemClock`, `port::CondVar`, TLS `Random`, and debug `SyncPoint`. Tests use it for deterministic or accelerated time behavior.

Risks and test signals: nondeterministic `TimedWait()` can expose races but makes exact wakeup assertions fragile. Overflow and monotonicity are assert-only. Tests should cover fake sleep increments, seconds/micros/nanos conversions, mutex release behavior, sync-point hooks, and callers that depend on timeout vs wakeup.
