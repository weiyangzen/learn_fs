# sources/user-network-fs/smblibrary/Utilities/Threading/CountdownLatch.cs

Purpose: `CountdownLatch` lets callers wait until an incremented count returns to zero.

Important APIs/types/functions: `Increment`, `Add`, `Decrement`, and `WaitUntilZero`.

Control flow: increments/adds adjust `m_count` atomically and reset the manual-reset event when transitioning from zero. Decrement decrements atomically, sets the event when count reaches zero, and throws if it goes negative.

State and persistence behavior: in-memory counter plus `EventWaitHandle`, initially signaled because count starts at zero.

Dependencies and integration points: uses `Interlocked` and `EventWaitHandle`; useful for coordinating worker completion.

Risks: `Decrement` checks `m_count == 0` rather than the local `count`, a minor race/read consistency smell. Negative decrement throws after decrementing, leaving count negative and the event state potentially inconsistent. The wait handle is never disposed.

Test signals: wait-until-zero behavior, add/increment transitions, negative decrement behavior, concurrent decrement race tests, and disposal expectations.
