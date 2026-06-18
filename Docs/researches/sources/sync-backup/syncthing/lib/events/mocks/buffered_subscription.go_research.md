## sources/sync-backup/syncthing/lib/events/mocks/buffered_subscription.go

Purpose: Counterfeiter-generated fake for `events.BufferedSubscription`.

Important APIs/types/functions: Fake `BufferedSubscription` implements `Mask` and `Since`, with stubs, counters, argument capture, default/per-call returns, and `Invocations`.

Control flow: Methods lock, record invocation, snapshot stub/returns, unlock, and return stub/default values. `Since` copies the input event slice argument for later inspection.

State and persistence: In-memory fake state protected by mutexes. No persistence.

Dependencies and integration points: Imports `events` and `time`; compile-time assertion satisfies `events.BufferedSubscription`.

Risks: Generated fake drift on interface changes; returned slices are not deep-copied.

Test signals: Compile-time conformance assertion.
