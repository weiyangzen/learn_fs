## sources/storage-engines/rocksdb/env/emulated_clock.h

### Purpose

`env/emulated_clock.h` declares `EmulatedSystemClock`, a `SystemClockWrapper` used by tests and configurable environments to simulate elapsed time and count sleep/CPU-time operations without necessarily slowing wall-clock execution.

### Important APIs, Types, And Functions

- `EmulatedSystemClock` wraps a base `SystemClock`.
- `SleepForMicroseconds()` increments `sleep_counter_`, optionally advances `addon_microseconds_`, and optionally delegates to real sleep.
- `MockSleepForMicroseconds()` and `MockSleepForSeconds()` advance mocked time without real sleeping when mock sleep is enabled.
- `SetTimeElapseOnlySleep()`, `SetMockSleep()`, `IsTimeElapseOnlySleep()`, and `IsMockSleepEnabled()` control time behavior.
- `GetCurrentTime()`, `NowMicros()`, and `NowNanos()` add mocked elapsed time to base or zero starting time.
- `CPUNanos()` and `CPUMicros()` count CPU-time calls, while `ResetCounters()` resets counters.

### Control Flow

When mock sleep or time-elapse-only-sleep mode is enabled, sleeps add their duration to `addon_microseconds_`. With `no_slowdown_` true, real sleeping is skipped; otherwise the call also delegates to the wrapped clock. Current time returns either a captured starting time or base clock time plus mocked seconds. Monotonic micro/nano time returns either zero or base time plus mocked microseconds.

### State And Persistence Behavior

The clock's state is in atomics: sleep count, CPU count, additional microseconds, and mode flags. It persists only in memory for the lifetime of the clock object. It deliberately warns that time-elapse-only-sleep should not be modified in the env of a running DB because timing changes can cause deadlocks or similar issues.

### Dependencies And Integration Points

It depends on `rocksdb/system_clock.h` and is registered as a built-in system clock in `env.cc` under class name `TimeEmulatedSystemClock`. It integrates with configurable `SystemClock::CreateFromString()` and `CompositeEnvWrapper` clock injection.

### Risks And Edge Cases

- `no_slowdown_` is a plain bool while other mode state is atomic; concurrent toggling during DB activity is explicitly discouraged.
- `GetCurrentTime()` converts mocked microseconds to whole seconds, while `NowMicros()`/`NowNanos()` preserve subsecond mocked time; tests must choose the right API.
- Time-elapse-only-sleep returns zero as the monotonic base, which can expose code that assumes nonzero wall-clock-like monotonic values.
- Mock sleep methods assert mock mode, so release builds may not enforce misuse as strongly as debug builds.

### Test Signals

Tests should verify no-slowdown sleep increments time and counters, real sleep mode delegates, current time advances by whole seconds, monotonic time advances by microseconds/nanoseconds, CPU counters increment, and configurable creation by class name works. Static research only; no test command was run.
