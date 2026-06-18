
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcScheduler.java

## Purpose

`RpcScheduler` defines the scheduling and backoff contract used by Hadoop IPC servers.

## Important APIs, types, and functions

`getPriorityLevel(Schedulable)` returns a priority hint. `shouldBackOff(Schedulable)` decides whether a caller should be throttled. The deprecated `addResponseTime(String, int, int, int)` exists for old implementations and throws by default. The modern default `addResponseTime(String, Schedulable, ProcessingDetails)` converts queue and processing timings to `RpcMetrics.TIMEUNIT` and delegates to the deprecated method. `stop()` releases scheduler resources.

## Control flow

Server call completion reports processing details to the scheduler. New implementations should override the modern method; old implementations can still receive queue/processing integers through the default bridge.

## State and persistence behavior

The interface has no state. Implementations such as `DecayRpcScheduler` maintain runtime metrics and timers.

## Dependencies and integration points

It integrates `Server.Call`, `Schedulable`, `ProcessingDetails`, `FairCallQueue`, and `RpcMetrics`.

## Risks and test signals

New schedulers that do not override the modern method will hit the deprecated default and likely throw. Tests should verify default bridge behavior, stop lifecycle, priority bounds, and backoff semantics for each scheduler implementation.
