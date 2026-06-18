# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestMiniOzoneCluster.java

## Purpose
`TestMiniOzoneCluster` verifies core MiniOzoneCluster and datanode lifecycle behavior in a local integration-test environment. It checks that clusters can start multiple HDDS datanodes, clients can connect to datanode container endpoints, random container ports are assigned uniquely, datanode restarts preserve advertised ports, datanodes recover registration after SCM restarts, and a custom datanode factory creates multiple data volumes with configured reserved space.

## Important APIs, Types, and Functions
- `MiniOzoneCluster.newBuilder(conf)` drives cluster construction through `setNumDatanodes`, `setDatanodeFactory`, `build`, `waitForClusterToBeReady`, `restartHddsDatanode`, and `restartStorageContainerManager`.
- `HddsDatanodeService`, `DatanodeStateMachine`, `EndpointStateMachine`, and `StorageContainerManager` expose the datanode and SCM state inspected by the tests.
- `Pipeline.newBuilder`, `PipelineID.randomId`, `StandaloneReplicationConfig.getInstance(ReplicationFactor.ONE)`, and `XceiverClientGrpc` create a one-datanode standalone pipeline and validate gRPC connectivity.
- Configuration keys under `OzoneConfigKeys`, `HddsConfigKeys`, and `ScmConfigKeys` control metadata directories, pipeline limit, random IPC/Ratis/datastream ports, and SCM stale-node timing.
- `UniformDatanodesFactory` and `StorageVolume` are used to assert volume count and reserved capacity.

## Control Flow
`setup` builds a shared `OzoneConfiguration` rooted at a JUnit temp directory, lowers the datanode pipeline limit, enables random Ratis IPC ports, and shortens SCM stale-node detection. Each test creates or manipulates a cluster and `cleanup` shuts it down if present. `testStartMultipleDatanodes` starts three datanodes, builds a standalone one-node pipeline for each, connects with `XceiverClientGrpc`, and asserts the selected node is connected. `testContainerRandomPort` constructs raw `DatanodeStateMachine` instances outside a full cluster, starts their read and write channels to force actual port binding, stops the channels, and verifies all read/write ports are nonzero and unique; it then disables the random IPC port flag and confirms multiple state machines use the same configured default read port. `testKeepPortsWhenRestartDN` captures all `DatanodeDetails.Port` values before and after a persistent datanode restart. `testDNstartAfterSCM` stops SCM, restarts a datanode, observes `GETVERSION`, restarts SCM, waits for readiness, and expects `HEARTBEAT`. `testMultipleDataDirs` starts one datanode with three data volumes and a one-byte reserved-space setting, then checks cluster naming/base-dir conventions and volume reservations.

## State and Persistence Behavior
The file exercises both ephemeral process state and persistent identity state. Port preservation relies on datanode restart with persisted metadata. The SCM restart path checks endpoint-state transitions rather than persisted tables. The multiple-volume test validates datanode volume configuration materialized into the container volume set. Random-port checks explicitly start container channels because port values are finalized only after server bind.

## Dependencies and Integration Points
The tests integrate MiniOzoneCluster with the HDDS datanode state machine, container read/write channels, SCM lifecycle, pipeline/client connectivity, temporary metadata directories, and volume usage accounting. `SCMTestUtils.getConf` provides a separate configuration for raw datanode-state-machine port checks.

## Risks and Edge Cases
Random port uniqueness is sensitive to bind timing and local port availability. The GETVERSION loop has no sleep, so it is a tight state assertion over a nominal twenty iterations rather than a true twenty-second wait. `testContainerRandomPort` sets the datastream-enabled flag on the shared `conf` instead of `ozoneConf`, which may be intentional for global defaults but is a configuration coupling worth watching. The tests do not write user data through OM; they focus on datanode and container-service surfaces.

## Test Signals
Strong signals include successful `XceiverClientGrpc` connection to every datanode, nonzero and unique random container channel ports, stable datanode port maps after restart, transition from `GETVERSION` to `HEARTBEAT` after SCM recovery, and exact data-volume count/reserved bytes. Failures usually indicate lifecycle, port binding, endpoint registration, or datanode factory regressions.
