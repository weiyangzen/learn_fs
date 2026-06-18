# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServer.java

## Purpose
`OzoneManagerRatisServer` wraps the Apache Ratis server used by OM HA. It constructs the Raft group, translates OM requests into Raft client requests, maps Raft replies and exceptions back to OM responses, manages dynamic peer configuration, and applies OM-specific Ratis configuration.

## Important APIs and Types
- `newOMRatisServer` builds a server from local node details, peer details, security config, and bootstrap mode.
- `submitRequest(OMRequest, boolean)` sends read or write OM requests through Ratis, subject to OM prepare-state gating.
- `submitRequest(OMRequest, ClientId, long)` supports internal submissions with explicit invocation IDs.
- Peer APIs include `addOMToRatisRing`, `removeOMFromRatisRing`, `addRaftPeer`, `removeRaftPeer`, `getPeers`, and `getPeerIds`.
- `createRaftPeer` preserves the configured host string instead of pre-resolving addresses so gRPC DNS refresh can work.
- `newRaftProperties` and helper setters populate Ratis log, RPC, retry cache, snapshot, close threshold, and HA properties.
- `RaftServerStatus` and `getLeaderStatus` expose leader readiness.

## Control Flow
Construction computes the storage directory, Raft group id from OM service id, peer map, state machine, read option, optional TLS parameters, and `RaftServer` instance. `submitRequest` rejects non-prepare/cancel writes when OM is prepared, otherwise creates a `RaftClientRequest`, submits it asynchronously to the local Ratis server, and converts the reply. Read requests use `getRaftReadRequestType`, honoring client read consistency hints where provided.

`createOmResponseImpl` handles unsuccessful replies by converting `NotLeaderException`, `LeaderNotReadyException`, `LeaderSteppingDownException`, read exceptions, and state-machine exceptions. For state-machine exceptions with an `OMException` cause, it builds a failed `OMResponse` with the mapped status; successful replies are decoded with `OMRatisHelper`.

Dynamic peer changes build `SetConfigurationRequest` objects from current follower/listener lists plus or minus the target node. Ratis config methods set log segment and preallocation sizes, purge behavior, appender queue limits, pending write element limits, RPC timeouts, retry cache expiry, auto snapshot threshold, and transport ports.

## State and Persistence Behavior
Persistent state is held by the underlying Ratis server in the configured Ratis storage directory. OM metadata persistence happens in the state machine/double buffer. This class tracks in-memory peer map, Raft group, state machine, client id, call id counter, and performance metrics.

## Dependencies and Integration Points
It integrates with `OzoneManager`, `OzoneManagerStateMachine`, `OMRatisHelper`, `OzoneManagerRatisUtils`, Ratis server/client classes, OM HA metrics, `SecurityConfig`, `CertificateClient`, and Hadoop/Ozone config keys. It is the submission path for OM RPC handlers and the owner of the state machine lifecycle.

## Risks and Edge Cases
Bootstrap mode starts with an empty peer list and relies on later set-configuration transactions. `getClientId` and `getCallId` require Hadoop RPC context unless test secure OM flag is set. State-machine exception mapping assumes causes are meaningful. `getRaftLeaderAddress` resolves the leader address for exception reporting, while peer creation intentionally avoids resolution for connectivity. Misconfigured HA properties can be passed through via prefix trimming.

## Test Signals
Tests should cover prepare-mode rejection, write/read request creation, read consistency hints, retry cache hits, not-leader and leader-not-ready conversion, state-machine exception status mapping, dynamic peer configuration, DNS-preserving peer creation, TLS parameter creation, and Ratis property defaults.
