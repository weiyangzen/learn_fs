<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/clock.go

Purpose: defines a tiny clock abstraction for code that needs timer behavior and test substitution.

Important APIs/types/functions: `Clock` interface with one method, `After(d time.Duration) <-chan time.Time`.

Control flow: no implementation is present in this file; callers depend only on the `After` contract. Real and fake implementations live in sibling files.

State and persistence: no state and no persistence. Implementations decide whether time is real, delayed, or simulated.

Dependencies and integration points: depends only on `time`. `RealClock`, `FakeClock`, and `SimulatedClock` implement this interface. The abstraction is useful for retry/backoff or wait logic where unit tests should avoid sleeping.

Risks: the interface only abstracts `After`, not `Now`, timers, tickers, or cancellation; call sites needing current time use other clock abstractions such as `timeutil.Clock` elsewhere in gcsfuse. Because returned channels are receive-only, implementations must decide buffering and close behavior consistently enough for callers.

Test signals: `simulated_clock_test.go` validates the richest implementation. No direct test is needed for this interface file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/clock.go -->
