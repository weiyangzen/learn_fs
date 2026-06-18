# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithAllRunning.java

## Purpose
Follower-read HA integration tests where all OM nodes stay running. It verifies follower proxy initialization, follower targeting, linearizable read consistency, normal object operations, response leader metadata, and read consistency mode metrics.

## Important APIs, types, and functions
- Uses `HadoopRpcOMFollowerReadFailoverProxyProvider`, `HadoopRpcOMFailoverProxyProvider`, `OMProxyInfo`, `OmTransport`, and `OzoneManagerProtocolClientSideTranslatorPB`.
- Exercises client APIs for volumes, buckets, files, deletes, and `headObject/listKeys`.
- Reads configs `OZONE_CLIENT_FOLLOWER_READ_ENABLED_KEY`, `OZONE_CLIENT_FOLLOWER_READ_DEFAULT_CONSISTENCY_KEY`, and `OZONE_CLIENT_LEADER_READ_DEFAULT_CONSISTENCY_KEY`.
- Directly submits protobuf `OMRequest` messages for suggested-leader and leader-node-id checks.

## Control flow
The suite first confirms follower-read proxy maps contain every OM RPC address and that a forced initial follower remains the last proxy after a read. It then checks write requests sent to a follower fail with `OMNotLeaderException` and suggested leader. Linearizable consistency uses a second client to immediately read keys written by the first client. Reused object-operation tests mirror the all-running HA suite. Later tests validate returned `leaderOMNodeId`, leader-only clients after leadership transfer, linearizable leader-read metrics, and local-lease follower-read metrics.

## State and persistence behavior
The tests create real volumes, buckets, keys, and directory-like paths in the HA OM metadata replicated through Ratis. They also observe metrics state on specific OM nodes: `NumLinearizableRead` on the leader and `NumFollowerReadLocalLeaseSuccess` on the selected follower/current proxy.

## Dependencies and integration points
This class covers the unified OM transport, separate leader and follower-read failover providers, OM Ratis leader status, client-side consistency configuration, object-store metadata APIs, and protobuf server translator behavior.

## Risks and edge cases
`testLinearizableReadConsistency` is marked flaky, showing timing sensitivity in cross-client read-after-write visibility. Tests that force proxy selection rely on test-only provider methods. Metrics assertions depend on a request hitting the expected node and consistency path.

## Test signals
Signals include exact proxy counts/address matches, last-proxy node ids, suggested-leader exception suffixes, immediate cross-client key visibility, expected file operation `OMException` codes, stable leader proxy state, and increasing read-consistency metrics.
