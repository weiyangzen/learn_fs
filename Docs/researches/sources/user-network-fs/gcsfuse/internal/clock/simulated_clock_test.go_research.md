<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go

Purpose: validates deterministic behavior of `SimulatedClock` for current time mutation and timer firing.

Important APIs/types/functions: tests `TestSimulatedClock_Now`, `TestSimulatedClock_SetTime`, `TestSimulatedClock_AdvanceTime`, `TestSimulatedClock_After_ShouldFireZeroOrNegativeDuration`, `TestSimulatedClock_After_ShouldFirePositiveDuration`, and `TestSimulatedClock_After_ShouldNotFire`; timeout constants `shortTestTimeout` and `fireTestTimeout`.

Control flow: table-driven tests initialize a clock with a fixed UTC time, call setup actions, then assert `Now`. Timer tests call `After`, manipulate simulated time by `AdvanceTime` or `SetTime`, and select on the returned channel versus a short real-time timeout.

State and persistence: test state is in-memory. Real timers are used only as guard timeouts to prevent blocking tests.

Dependencies and integration points: uses `testify/assert` and `require`. It covers the clock implementation used by testable wait logic in the local `internal/clock` package.

Risks: real-time timeout constants are small; heavily loaded CI could theoretically cause false negatives in firing tests, though simulated firing itself is synchronous after clock mutation. The tests do not include concurrent access, multiple pending timers, or time moving backward with pending timers.

Test signals: confirms non-positive durations fire immediately with the current time, positive timers fire with the scheduled target time rather than the later current time, and timers do not fire before their target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go -->
