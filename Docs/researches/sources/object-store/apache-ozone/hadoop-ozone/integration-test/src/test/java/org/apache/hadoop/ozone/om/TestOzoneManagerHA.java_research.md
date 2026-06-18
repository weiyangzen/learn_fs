# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHA.java

## Purpose
Abstract base for standard OM HA integration tests. It initializes the shared HA cluster without follower-read mode and provides a helper to stop the current leader.

## Important APIs, types, and functions
- Extends `AbstractOzoneManagerHATest`.
- Static `init` calls `initCluster(false)`.
- `stopLeaderOM` uses `OmTestUtil.getCurrentOmProxyNodeId(getObjectStore())` and `getCluster().stopOzoneManager(nodeId)`.

## Control flow
Subclasses inherit a ready HA cluster from `@BeforeAll`. When a test needs failover, `stopLeaderOM` asks the client failover proxy which OM is currently serving as leader and stops that node.

## State and persistence behavior
The base does not mutate metadata directly. It controls cluster process state by stopping OM nodes while preserving the shared HA metadata/Ratis state managed by `AbstractOzoneManagerHATest`.

## Dependencies and integration points
It binds subclass tests to the common HA harness, object store client failover provider, MiniOzoneHACluster node control, and OM leader discovery utilities.

## Risks and edge cases
Because the helper trusts the current client proxy node, stale proxy state can stop a node that was leader from the client's view rather than the cluster's latest leader. Subclasses typically wait for leader readiness around node restarts.

## Test signals
This base has no assertions of its own; its signal is successful cluster initialization and correct behavior of subclasses that depend on stopping the leader.
