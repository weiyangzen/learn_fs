
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcScheduler.java

## Purpose

`DecayRpcScheduler` is the non-default RPC scheduler that assigns calls to priority levels based on decayed per-identity call cost. It tracks caller cost over time, periodically decays historical cost, computes queue priorities, optionally backs off lower-priority callers when recent response time is high, and exports scheduler state through JMX and Metrics2.

## Important APIs, types, and functions

The class implements `RpcScheduler`, `DecayRpcSchedulerMXBean`, and `MetricsSource`. Its constructor reads namespace-scoped configuration for decay period, decay factor, thresholds, identity provider, cost provider, response-time backoff, and top-user metric count. `getPriorityLevel(Schedulable)` returns a queue index, `shouldBackOff(Schedulable)` evaluates response-time backoff, `addResponseTime()` records both call cost and queue/processing latency, and `stop()` unregisters metrics. Package-visible helpers such as `forceDecay()`, `getThresholds()`, and `getCallCostSnapshot()` are test hooks.

`DecayTask` is a weak-reference `TimerTask` that drives periodic decay. `MetricsProxy` is a namespace singleton that keeps a weak delegate and exposes `DecayRpcSchedulerMXBean`/`MetricsSource` without pinning old scheduler instances.

## Control flow

Construction validates `numLevels`, parses config, creates response-time arrays, schedules a daemon `Timer`, installs a metrics proxy, and initializes the scheduling cache. Incoming completed calls enter through `addResponseTime()`: the identity and cost are computed, raw and decayed counters are incremented, then response-time totals for the call's current priority are accumulated. `getPriorityLevel()` normalizes identity, checks the immutable cache, and computes a fallback priority when the cache has no entry.

Each timer tick runs `decayCurrentCosts()`. It multiplies each decayed cost by `decayFactor`, removes identities whose decayed cost reaches zero, recomputes total decayed/raw volumes, atomically swaps a new unmodifiable decision cache, and rolls current-window response-time totals into last-window averages. Priority computation compares the identity's decayed-cost share against thresholds from highest level down.

## State and persistence behavior

All state is in-memory. `callCosts` maps identity to two `AtomicLong`s: decayed cost and raw cost. Totals are held in `AtomicLong`s; response-time metrics are in atomic arrays; `scheduleCacheRef` points at the latest read-only decision map. Static priorities are stored in a plain `HashMap` for special users. No scheduler state is persisted across process restart.

## Dependencies and integration points

The scheduler plugs into `Server` through the `RpcScheduler` interface and into `FairCallQueue` via `Schedulable.getPriorityLevel()`. Identity and cost are supplied by configurable `IdentityProvider` and `CostProvider` implementations, defaulting to `UserIdentityProvider` and `DefaultCostProvider`. Metrics integrate with `DefaultMetricsSystem`, `MBeans`, `RpcMetrics.TIMEUNIT`, and Jackson JSON summaries.

## Risks and test signals

Concurrency risk centers on maintaining consistency between per-identity atomics, totals, and the periodically swapped cache; stale scheduling decisions are expected between decay sweeps. `staticPriorities` is a non-concurrent `HashMap`, so external priority mutation should be limited. `getIdentity()` maps null provider output to `IdentityProvider.Unknown`, but `addResponseTime()` calls `identityProvider.makeIdentity()` directly before `addCost()`, so custom providers returning null can create a null key. Tests should cover config validation, deprecated key fallback, threshold math, decay cleanup, static priority clamping, response-time backoff, metrics/JMX proxy replacement, and local Ozone signals such as `TestDecayRpcSchedulerUtil`.
