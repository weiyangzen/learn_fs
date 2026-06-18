# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SlidingWindow.java

## Purpose
Tracks recent events with both time expiry and a maximum window size, useful for rate or burst accounting.

## Important APIs, Types, And Functions
`SlidingWindow` exposes `add`, `isExceeded`, `getNumEvents`, `getNumEventsInWindow`, `getWindowSize`, and `getExpiryDurationMillis`. A nested `MonotonicClock` uses `System.nanoTime()` converted to milliseconds.

## Control Flow
Construction validates non-negative size and positive expiry, then creates an `ArrayDeque` with bounded initial capacity. `add()` first calls `isExceeded()` and removes one oldest timestamp if already exceeded, then appends the current time. Queries synchronize on a private lock, prune expired timestamps, and compute size or capped size.

## State And Persistence
State is an in-memory deque of millisecond timestamps plus clock and config. There is no persistence. Synchronization protects deque mutation.

## Dependencies And Integration Points
Depends on Java time APIs and `@VisibleForTesting`. The custom clock supports deterministic tests.

## Risks
The constructor permits `windowSize == 0` although its error text says greater than 0; this makes every event exceed the window and `add()` can remove before adding. Expiry uses `< expirationThreshold`, so exact-boundary events remain. Nested synchronization is reentrant but redundant.

## Test Signals
`TestSlidingWindow` covers validation, expiry, max-size behavior, zero-size behavior, and custom-clock advancement. Concurrency tests would add confidence for simultaneous add/query use.
