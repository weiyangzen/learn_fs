# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/TestClock.java

Purpose: `TestClock` is a mutable `java.time.Clock` implementation for tests that need deterministic control over current time.

Important APIs and types: It extends `Clock` and exposes `newInstance`, constructor `(Instant, ZoneId)`, `getZone`, `withZone`, `instant`, `fastForward(long)`, `fastForward(TemporalAmount)`, `rewind(long)`, `rewind(TemporalAmount)`, and `set(Instant)`.

Control flow: `instant` returns the stored instant. Fast-forward and rewind compute a new instant by adding or subtracting milliseconds or a temporal amount, then delegate to `set`.

State and persistence behavior: Runtime state is mutable `instant` plus immutable `zoneId`. There is no persistence.

Dependencies and integration points: Used by tests for timeouts, stale container detection, lifecycle timestamps, and services that accept an injected `Clock`.

Risks: `withZone` returns a new clock using `Instant.now()` rather than preserving the current test instant, which can surprise callers expecting standard `Clock.withZone` semantics. It is mutable and not synchronized.

Test signals: Consumers assert time-dependent transitions after explicit `fastForward`, `rewind`, or `set` calls without sleeping.
