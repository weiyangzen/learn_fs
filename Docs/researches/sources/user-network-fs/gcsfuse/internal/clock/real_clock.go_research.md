<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go

Purpose: production implementation of the local `Clock` interface backed by Go's wall-clock timer.

Important APIs/types/functions: `RealClock` empty struct and method `After(d time.Duration) <-chan time.Time`.

Control flow: `After` delegates directly to `time.After(d)` and returns its channel.

State and persistence: stateless wrapper; timer state is owned by the Go runtime. No persistence.

Dependencies and integration points: depends only on `time` and implements `Clock`. It is the natural production counterpart to `FakeClock` and `SimulatedClock` for code that depends on the package-local clock abstraction.

Risks: `time.After` allocates a timer that cannot be canceled by the caller through this interface. Repeated long-duration waits in loops can retain timers until they fire. This is a limitation of the minimal `Clock` interface rather than this wrapper specifically.

Test signals: no direct test in this subset; behavior is Go standard library behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go -->
