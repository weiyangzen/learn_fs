<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go

Purpose: implements a deterministic, manually advanced clock for unit tests that need `After` behavior without sleeping.

Important APIs/types/functions: internal `afterRequest`, `SimulatedClock` with guarded fields `t` and `pending`, constructor `NewSimulatedClock`, methods `Now`, `SetTime`, `AdvanceTime`, `After`, and helper `processPending`.

Control flow: `Now` returns the guarded current simulated time. `SetTime` replaces the time and processes pending timers. `AdvanceTime` adds a duration and processes pending timers. `After` creates a buffered one-element channel, computes `targetTime = current + d`, immediately sends current time for non-positive durations, or appends a pending request. `processPending` scans requests and sends `targetTime` for each request whose target is reached, retaining only future requests.

State and persistence: state is in-memory and protected by `sync.RWMutex`. Pending requests are held until fired or until the clock is discarded. Channels are not closed, matching `time.After` behavior.

Dependencies and integration points: depends on `sync` and `time`, implements the package `Clock` interface, and adds `Now`/time-control methods for tests.

Risks: moving time backward with `SetTime` is allowed and can leave existing future timers pending longer in simulated time. There is no cancellation/removal API. Sending while holding the lock is safe because channels are buffered, but changing buffer behavior would risk deadlocks. Fired timer values are scheduled target times, while immediate non-positive durations send current time.

Test signals: `simulated_clock_test.go` covers `Now`, `SetTime`, positive/negative/zero advances, immediate timers, firing by set/advance past target, and non-firing before target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go -->
