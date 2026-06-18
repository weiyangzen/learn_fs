# sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.cpp

## Purpose
`RatekeeperMonitor.cpp` implements the cluster-controller helper that detects whether ratekeeper has continuously reported a zero TPS limit long enough to justify failover behavior. It also contains a focused Flow unit test for the sustained-zero detection logic.

## Important APIs, Types, and Functions
- `RatekeeperMonitor::hasSustainedZeroRatekeeperTpsLimit(double tpsLimit, double currentTime, double zeroTpsLimitDuration)` is the only implemented production method in this file.
- The unit test `TEST_CASE("/fdbserver/clustercontroller/hasSustainedZeroRatekeeperTpsLimit")` validates first-observation, threshold, reset, restart, and disabled-duration behavior.

## Control Flow
`hasSustainedZeroRatekeeperTpsLimit()` first resets observation and returns false if the configured duration is non-positive or the current TPS limit is positive. If the limit is zero and this is the first zero observation, it stores `currentTime` and returns false. On later zero observations, it returns true only when `currentTime - zeroRatekeeperTpsLimitStartTime >= zeroTpsLimitDuration`.

The test constructs a monitor, observes a zero limit at time 100, verifies no immediate sustained result, verifies threshold behavior just before and at 5 seconds, verifies a positive TPS limit clears the start time, verifies a new zero window starts at time 107, and verifies duration `0.0` disables detection and clears state.

## State and Persistence Behavior
The implementation has no durable persistence. It mutates only the in-memory optional `zeroRatekeeperTpsLimitStartTime` field owned by `RatekeeperMonitor`. Reset happens on positive TPS limits and disabled/invalid duration. The caller controls time by passing `currentTime`; the header default uses `now()`.

## Dependencies and Integration Points
The source includes `RatekeeperMonitor.h` and `flow/UnitTest.h`. The monitor is intended for cluster-controller logic that evaluates ratekeeper health or throttling state, using `SERVER_KNOBS->CC_FAILOVER_DUE_TO_TPS_LIMIT_DURATION` by default through the header declaration.

## Risks and Edge Cases
- The function treats any `tpsLimit <= 0` as zero/sustained candidate; negative values are not distinguished from zero.
- Non-monotonic `currentTime` can delay detection because elapsed duration is computed directly from the first observation.
- A non-positive duration disables the observation and clears state, which is useful for a knob-off mode but can surprise callers expecting immediate detection.
- The monitor tracks only one continuous window and has no smoothing or tolerance for brief positive blips.

## Test Signals
The embedded Flow unit test provides direct coverage of the state machine. Additional integration tests should verify the cluster-controller failover path that consumes this monitor, especially that ratekeeper recovery to positive TPS cancels any pending failover decision.
