# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/common/TestEndPoint.java

Purpose: This integration-heavy test suite validates datanode endpoint RPC tasks against a mock SCM RPC server. It covers version negotiation, datanode registration, heartbeat processing, command-status creation, datanode layout storage, deleted-container cleanup, cluster-ID mismatch handling, invalid endpoints, and RPC timeout behavior.

Important APIs and types: The suite uses `EndpointStateMachine`, `VersionEndpointTask`, `RegisterEndpointTask`, `HeartbeatEndpointTask`, `DatanodeStateMachine`, `StateContext`, `OzoneContainer`, `MutableVolumeSet`, `HddsVolume`, `DatanodeLayoutStorage`, `ScmTestMock`, `SCMTestUtils`, Hadoop `RPC.Server`, storage report protos, heartbeat/register/version protos, `CommandStatus`, and SCM command protos for close, replicate, and delete-block commands.

Control flow: `@BeforeAll` creates configuration, initializes datanode layout storage, starts a mock SCM RPC server, captures its address, and selects a volume policy. Tests create endpoint state machines against valid or invalid addresses, set expected endpoint states, call the endpoint task, and assert state transitions. Helpers create volumes, add schema-v3 containers, move containers to deleted paths, construct register tasks, and run heartbeat tasks with a temporary datanode state machine.

State and persistence behavior: The test writes real datanode layout VERSION files, hdds volume directories, container files and DB paths, and deleted-container temp directories. It verifies cleanup of deleted container directories on version task startup, cluster ID persistence in layout storage, failed-volume movement on mismatched cluster IDs, and in-memory command-status map updates from heartbeat responses.

Dependencies and integration points: It joins SCM RPC protocol handling, datanode state-machine endpoint tasks, layout-version negotiation, volume formatting, key-value container utility paths, container reports, pipeline reports, node reports, replication server configuration, and log capture.

Risks: Timing and port behavior are important: tests set random ports and use bounded RPC timeouts. Global `scmServerImpl` response-delay and cluster-ID mutations must be reset carefully. Some tests compare elapsed time with tolerances and one heartbeat timeout allows extra shutdown delay.

Test signals: Signals include version response description keys, endpoint state transitions GETVERSION to REGISTER to HEARTBEAT, invalid endpoint state retention, SHUTDOWN on missing datanode details or cluster mismatch, empty deleted-container directory, layout cluster ID values, register container/node report counts, heartbeat command counts, command-status map entry for delete blocks command ID 3, and elapsed time below timeout tolerance.
