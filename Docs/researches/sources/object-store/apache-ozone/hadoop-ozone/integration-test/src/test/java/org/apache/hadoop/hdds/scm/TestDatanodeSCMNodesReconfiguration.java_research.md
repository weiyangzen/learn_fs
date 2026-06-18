# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestDatanodeSCMNodesReconfiguration.java

## Purpose

`TestDatanodeSCMNodesReconfiguration` validates dynamic datanode reconfiguration of SCM peer lists in HA clusters. It covers SCM migration/decommission and adding/removing an SCM node while datanodes are running.

## Important APIs, Types, And Functions

The class uses `MiniOzoneHAClusterImpl`, `HddsDatanodeService`, `StorageContainerManager`, `ConfUtils`, SCM node keys, reconfiguration handlers, datanode connection managers, queue metrics, and `DecommissionScmResponseProto`. Helpers include `decommissionSCM` and `assertIsPropertyReconfigurable`.

## Control Flow

Setup starts a three-SCM HA cluster with datanodes. `testSCMMigration` decommissions SCM peers and validates that datanode SCM connections, queue metrics, and endpoint state machines converge to the reduced peer set. `testAddAndRemoveOneSCM` bootstraps an additional SCM, pushes new SCM address properties into datanode configs, triggers reconfiguration, waits for registration, then removes the SCM and waits for stale/dead accounting.

## State And Persistence Behavior

The test mutates SCM HA membership, datanode runtime configuration, connection-manager state, queue metrics, and node-health records. SCM decommission also changes Ratis peer configuration and active SCM membership.

## Dependencies And Integration Points

It integrates SCM HA bootstrap/decommission, datanode reconfiguration, SCM datanode protocol connections, heartbeat queues, and node manager health state.

## Risks And Test Signals

The test is asynchronous and timeout-sensitive. Failures point to non-reconfigurable keys, leaked SCM connections, incorrect queue/executor sizing, failed datanode registration to new SCMs, or stale peer membership after decommission.
