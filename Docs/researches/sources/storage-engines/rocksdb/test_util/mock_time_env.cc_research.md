# sources/storage-engines/rocksdb/test_util/mock_time_env.cc

Purpose: implements the platform-specific part of `MockSystemClock`, currently `InstallTimedWaitFixCallback()`, a debug-build workaround for timed wait behavior differences.

Important API/control flow: in non-release builds it disables sync-point processing, clears callbacks, and on macOS registers a callback at `InstrumentedCondVar::TimedWaitInternal`. The callback rewrites an already-expired deadline to a real-clock deadline one millisecond in the future, then sync-point processing is re-enabled.

State and dependencies: mutates global `SyncPoint` callback state. It depends on `test_util/sync_point.h` and `MockSystemClock::RealNowMicros()`. No durable state is written.

Integration points: used by tests that run against mock time but still pass deadlines to platform condition variables interpreted against real time.

Risks and test signals: this helper globally clears callbacks, so callers must install it before adding test-specific sync points or accept that existing callbacks are removed. It is disabled in release builds and only changes macOS behavior. Tests should verify no deadlock when a mocked deadline is already elapsed and that non-macOS builds leave deadlines unchanged.
