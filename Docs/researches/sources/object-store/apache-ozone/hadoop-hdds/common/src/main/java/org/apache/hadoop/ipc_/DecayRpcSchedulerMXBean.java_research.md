
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DecayRpcSchedulerMXBean.java

## Purpose

This interface defines the JMX view for `DecayRpcScheduler`. It exposes scheduling decisions, call volume, identity count, response-time averages, and last-window call counts to operators and metrics proxies.

## Important APIs, types, and functions

The API is read-only: `getSchedulingDecisionSummary()`, `getCallVolumeSummary()`, `getUniqueIdentityCount()`, `getTotalCallVolume()`, `getAverageResponseTime()`, and `getResponseTimeCountInLastWindow()`.

## Control flow

There is no local control flow. `DecayRpcScheduler` and its `MetricsProxy` implement this interface, with the proxy delegating to the active scheduler when its weak reference is still live.

## State and persistence behavior

The interface owns no state. Implementations return in-memory scheduler snapshots, usually arrays copied from atomic arrays or JSON derived from current maps.

## Dependencies and integration points

It is registered as an MBean by `DecayRpcScheduler.MetricsProxy` under the scheduler namespace. Consumers are JMX/metrics tooling and tests that inspect scheduler behavior.

## Risks and test signals

Array-returning methods should return snapshots rather than mutable internal arrays. Tests should verify proxy behavior after scheduler replacement or garbage collection and confirm summaries remain valid JSON or clear error strings.
