
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Schedulable.java

## Purpose

`Schedulable` is the minimal call metadata contract consumed by RPC schedulers and fair queues.

## Important APIs, types, and functions

`getUserGroupInformation()` returns the remote user. `getCallerContext()` defaults to throwing `UnsupportedOperationException` and is intended to be overridden by `Server.Call`. `getPriorityLevel()` returns the call's assigned priority.

## Control flow

Schedulers inspect a `Schedulable` to derive identities and priority decisions. `FairCallQueue` reads `getPriorityLevel()` to choose a subqueue.

## State and persistence behavior

The interface has no state. Implementations carry per-call user, caller context, and priority metadata in memory.

## Dependencies and integration points

It depends on `UserGroupInformation` and optional `CallerContext`. It is implemented by server calls and by scheduler test/dummy objects.

## Risks and test signals

Callers must not assume `getCallerContext()` is always supported. Tests should cover UGI extraction, priority propagation into `FairCallQueue`, and fallback behavior for schedulable implementations that only provide UGI and priority.
