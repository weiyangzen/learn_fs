
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/DefaultRpcScheduler.java

## Purpose

`DefaultRpcScheduler` is the no-op scheduler implementation. It keeps all calls at priority `0`, never asks callers to back off, and ignores response-time reporting.

## Important APIs, types, and functions

The constructor accepts the same shape as configurable schedulers but stores nothing. `getPriorityLevel()` returns `0`, `shouldBackOff()` returns `false`, `addResponseTime()` is empty, and `stop()` is empty.

## Control flow

Server setup can instantiate this scheduler as a drop-in when prioritization is disabled. Calls pass through without changing queue placement or backoff behavior.

## State and persistence behavior

There is no mutable or persistent state.

## Dependencies and integration points

It implements `RpcScheduler` and serves as the compatibility baseline for `Server`/`CallQueueManager` integrations.

## Risks and test signals

The risk is configuration drift: deployments expecting fair queuing receive FIFO-equivalent priority hints if this scheduler is selected. Tests should verify zero-priority/no-backoff behavior and that `stop()` is harmless.
