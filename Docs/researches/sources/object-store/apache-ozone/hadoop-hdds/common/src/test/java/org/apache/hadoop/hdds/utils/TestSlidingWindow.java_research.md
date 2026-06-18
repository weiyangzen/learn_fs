# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSlidingWindow.java

## Purpose
Tests `SlidingWindow` event counting/expiration behavior with a controllable clock.

## Important APIs, types, and functions
- Uses `SlidingWindow`, `Duration`, and `TestClock`.
- Covers constructor validation, adding events, full expiration, partial expiration, and zero window size.

## Control flow
Setup creates a test clock and sliding window. Tests add events, advance time, and assert window counts after no expiration, partial expiration, complete expiration, and zero-duration cases.

## State and persistence behavior
State is in-memory timestamped event buckets. No persistence.

## Dependencies and integration points
Sliding-window counters are useful for rate or recent-event tracking in HDDS utilities.

## Risks and test signals
Boundary mistakes can overcount or undercount recent activity. The tests signal time-window edge behavior using deterministic time.
