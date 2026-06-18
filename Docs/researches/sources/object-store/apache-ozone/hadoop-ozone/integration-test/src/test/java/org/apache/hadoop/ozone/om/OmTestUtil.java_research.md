# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OmTestUtil.java

## Purpose
`OmTestUtil` exposes static utilities for inspecting OM RPC failover internals from an `ObjectStore`. It helps tests verify which OM proxy is active and access follower-read failover providers.

## Important APIs, Types, and Functions
- `getFailoverProxyProvider(ObjectStore store)` unwraps the object-store client proxy to `OzoneManagerProtocolClientSideTranslatorPB`, then to `Hadoop3OmTransport`, and returns the HA failover proxy provider.
- `getFollowerReadFailoverProxyProvider(ObjectStore store)` returns the follower-read failover proxy provider from the same transport.
- `getCurrentOmProxyNodeId(ObjectStore store)` returns the current proxy OM node ID.

## Control Flow
Each method performs downcasts through the client proxy transport stack and returns provider state. There is no retry or fallback logic; it assumes the store uses the Hadoop 3 OM transport.

## State and Persistence Behavior
No persistent state is modified. The methods inspect client-side routing state maintained by the failover provider.

## Dependencies and Integration Points
The utility integrates `ObjectStore`, `OzoneManagerProtocolClientSideTranslatorPB`, `Hadoop3OmTransport`, `HadoopRpcOMFailoverProxyProvider`, and `HadoopRpcOMFollowerReadFailoverProxyProvider`.

## Risks and Test Signals
The main risk is brittle downcasting if the client transport implementation changes. Its signals are direct access to current proxy node IDs and failover provider objects for HA/follower-read assertions.
