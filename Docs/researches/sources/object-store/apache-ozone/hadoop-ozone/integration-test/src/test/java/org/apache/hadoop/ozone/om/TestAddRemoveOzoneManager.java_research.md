# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestAddRemoveOzoneManager.java

## Purpose
`TestAddRemoveOzoneManager` exercises dynamic OM HA membership: bootstrapping voting OMs, bootstrapping listener OMs, forced bootstrap behavior, decommissioning, authorization, listener leadership safety, mixed voting/listener clusters, and listener removal.

## Important APIs, Types, and Functions
- `setupCluster(...)` creates an HA cluster, optionally enables test authorization, creates a volume/bucket/key, and records the leader's last applied transaction index.
- `getCurrentPeersFromRaftConf(...)`, `assertNewOMExistsInPeerList(...)`, and `assertNewOMExistsInListenerList(...)` validate OM peer/listener state and Ratis log catch-up.
- `testBootstrapOMs(...)` and `testBootstrapListenerOMs(...)` call `cluster.bootstrapOzoneManager(...)`.
- `decommissionOM(...)` updates `OZONE_OM_DECOMMISSIONED_NODES_KEY`, pushes config to active OMs, calls `OMAdminProtocolClientSideImpl.decommission`, waits for peer removal, and waits for leader election.
- Test methods cover normal bootstrap, missing config failures, force bootstrap, listener bootstrap/decommission, decommission authorization, listener non-leadership, mixed node types, and listener removal.

## Control Flow
The tests start from one-, two-, or three-OM clusters, add new OMs with different flags, and validate both high-level OM peer lists and underlying Ratis peer/listener configuration. Failure tests capture logs and assert expected exception messages/system-exit messages. Decommission tests modify configuration, create an admin protocol client under a selected `UserGroupInformation`, issue decommission, and then check live cluster operations still succeed.

## State and Persistence Behavior
The file mutates HA membership state, Ratis raft configuration, OM peer-node lists, decommissioned-node config, local Ratis log directories, and OM metadata state used to verify new nodes catch up. It also depends on user authorization state when test authorization is enabled.

## Dependencies and Integration Points
Major integrations are `MiniOzoneHAClusterImpl`, OM bootstrap APIs, `OzoneManagerRatisServer`, Ratis `RaftPeer` and listener configuration, `OMAdminProtocolClientSideImpl`, `UserGroupInformation`, `GenericTestUtils.waitFor`, log capture, and `TestOzoneManagerHA.createKey`.

## Risks and Test Signals
Risks include flaky timing around Ratis leader election and log replication, exact log-message assertions, and authorization context leakage. Signals include new node presence in peer/listener lists, Ratis logs on bootstrapped OMs, last-applied index catch-up, leader election by a new voting OM, listener nodes not becoming leaders, successful reads/writes after membership changes, and peer/listener removal after decommission.
