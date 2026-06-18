# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeNotFoundException.java

## Purpose
`NodeNotFoundException` signals that a requested datanode ID is absent from `NodeStateMap`.

## Important APIs, Types, And Functions
It extends `NodeException` and has no-argument and `DatanodeID` constructors. The ID constructor formats `Datanode <id> not found`.

## Control Flow
`NodeStateMap.getExisting` throws it, and many read/update/remove operations propagate it. Higher-level managers either surface it, translate it into warnings, or treat it as a stale report.

## State And Persistence Behavior
The exception is transient and contains only message state.

## Dependencies And Integration Points
It depends on `DatanodeID` and appears throughout `SCMNodeManager`, placement providers, and report handlers where node membership is looked up.

## Risks And Edge Cases
Some higher-level methods convert not-found to null or logs, while others propagate it. Callers need to know whether absence is exceptional, a stale heartbeat/report, or expected during concurrent removal.

## Test Signals
Tests should verify missing node paths in `NodeStateMap`, `SCMNodeManager` report handling, EC read-pipeline creation, and removal race handling.
