# sources/storage-engines/foundationdb/fdbserver/clustercontroller/RatekeeperMonitor.h

## Purpose
`RatekeeperMonitor.h` declares a small stateful helper used by cluster-controller code to track how long ratekeeper has advertised a zero TPS limit. The helper abstracts the duration calculation and reset behavior behind a single monitor class.

## Important APIs, Types, and Functions
- `RatekeeperMonitor::resetZeroRatekeeperTpsLimitObservation()` clears any active zero-limit observation.
- `RatekeeperMonitor::hasSustainedZeroRatekeeperTpsLimit()` evaluates whether a zero TPS limit has lasted at least the configured duration. Defaults use `now()` and `SERVER_KNOBS->CC_FAILOVER_DUE_TO_TPS_LIMIT_DURATION`.
- `RatekeeperMonitor::getZeroRatekeeperTpsLimitDuration()` returns elapsed time since the active zero observation or `0.0` when no observation is active.
- `RatekeeperMonitor::getZeroRatekeeperTpsLimitStartTime()` exposes the optional start time for tests and diagnostics.

## Control Flow
The header exposes a caller-driven polling model. Callers feed ratekeeper's current TPS limit into `hasSustainedZeroRatekeeperTpsLimit()`. Positive limits or disabled duration reset the monitor. Continuous zero-limit calls first set the start time, then later report true when the elapsed duration reaches the threshold. Consumers can separately inspect elapsed duration for status reporting.

## State and Persistence Behavior
The class stores one private field, `Optional<double> zeroRatekeeperTpsLimitStartTime`. It has no persistent storage, no actor ownership, and no concurrency control. It assumes calls are made from the owning cluster-controller context.

## Dependencies and Integration Points
The header includes `fdbserver/core/Knobs.h` for the default failover duration, `flow/Optional.h`, and `flow/flow.h` for `now()`. It forward declares `ClusterControllerData`, though this declaration is not used directly in the class. The likely integration point is cluster-controller monitoring/recruitment logic that observes ratekeeper limits and decides whether zero throughput is sustained enough to trigger failover.

## Risks and Edge Cases
- Because default arguments call global time and knob state, tests should pass explicit `currentTime` and duration when deterministic behavior is needed.
- The class is intentionally minimal and does not track ratekeeper identity. If ratekeeper is re-recruited, callers should reset or recreate the monitor to avoid carrying a zero-limit window across role instances unless that behavior is intended.
- Optional elapsed duration returns `0.0` for both no active observation and an observation whose start time equals current time; callers needing that distinction should inspect `getZeroRatekeeperTpsLimitStartTime()`.

## Test Signals
The implementation file contains a unit test for the public state transitions. Integration-level test signals should include failover not firing before the knob duration, firing at or after the duration, and clearing after positive TPS or knob disablement.
