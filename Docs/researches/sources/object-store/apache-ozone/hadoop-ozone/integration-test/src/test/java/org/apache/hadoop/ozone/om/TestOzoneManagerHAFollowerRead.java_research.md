# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerRead.java

## Purpose
Abstract base for OM HA tests with follower-read mode enabled. It centralizes cluster initialization and the expected read failure handling when quorum or connectivity is unavailable.

## Important APIs, types, and functions
- Extends `AbstractOzoneManagerHATest`.
- Static `init` calls `initCluster(true)`.
- `listVolumes(boolean checkSuccess)` calls `getObjectStore().getClientProxy().listVolumes(null, null, 100)` and validates acceptable failures.

## Control flow
Subclasses start from a follower-read-enabled HA cluster. `listVolumes(false)` permits several failure shapes: a `RemoteException` wrapping a Ratis `RaftException`, a `ConnectException` with connection refused, or a leader-determination/connectivity message. `listVolumes(true)` rethrows unexpected IO failures.

## State and persistence behavior
No metadata is created here. The base focuses on read consistency/failure semantics under changing cluster availability and lets subclasses drive OM node state.

## Dependencies and integration points
It integrates the Ozone client proxy, follower-read HA mode, Hadoop IPC `RemoteException`, Java network exceptions, and Ratis read-index/read-timeout exception surfaces.

## Risks and edge cases
The accepted failure messages/classes encode client retry ordering and last-proxy behavior; changes in retry policy can alter which exception is observed. It intentionally checks broad message alternatives for non-RemoteException cases.

## Test signals
The reusable signal is that successful list-volume reads complete silently, while expected degraded-cluster failures are classified as Ratis quorum/read failures or connection failures.
