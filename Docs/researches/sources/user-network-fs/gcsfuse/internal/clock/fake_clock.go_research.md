<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go

Purpose: implements the `Clock` interface with a fixed real-time sleep duration for tests that need predictable shortened waits.

Important APIs/types/functions: `FakeClock` struct with `WaitTime time.Duration`, and method `After(time.Duration) <-chan time.Time`.

Control flow: `After` ignores the requested duration, creates an unbuffered channel, starts a goroutine, sleeps for `WaitTime`, and sends `time.Now()` on the channel.

State and persistence: state is only the configured `WaitTime`. There is no persistence and no tracking of outstanding timers beyond goroutines blocked on channel send.

Dependencies and integration points: depends on `time` and implements `Clock` from `clock.go`. It is appropriate for tests that need wait operations to complete faster than production, but still use wall-clock sleeping.

Risks: because the returned channel is unbuffered, the goroutine can remain blocked if the caller never receives. Ignoring the input duration is useful for tests but can hide bugs in code that relies on varying durations. It uses real wall-clock time, so tests using it can still be flaky under scheduler delays.

Test signals: no direct tests in this subset. `SimulatedClock` provides more deterministic timer test coverage and is preferable when exact scheduling semantics matter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go -->
