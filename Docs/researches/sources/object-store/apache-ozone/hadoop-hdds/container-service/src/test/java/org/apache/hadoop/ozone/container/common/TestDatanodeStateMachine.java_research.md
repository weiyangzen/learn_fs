# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStateMachine.java

Purpose: This suite validates datanode state machine startup, INIT-to-RUNNING transitions, SCM endpoint RPC sequencing, failure-to-write ID handling, invalid SCM configuration handling, daemon stop, and thread priority ordering.

Important APIs and types: It uses `DatanodeStateMachine`, `DatanodeStateMachine.DatanodeStates`, `InitDatanodeState`, `RunningDatanodeState`, `EndpointStateMachine`, `SCMConnectionManager`, `ScmTestMock`, `SCMTestUtils`, `DatanodeLayoutStorage`, `HDDSLayoutFeature`, `ContainerUtils.writeDatanodeDetailsTo`, `CapacityVolumeChoosingPolicy`, Hadoop `RPC.Server`, and executor services from `HadoopExecutors`.

Control flow: `setUp` creates an Ozone config rooted in a temp directory, enables random IPC and Ratis ports, starts one mock SCM RPC server, and prepares a daemon executor. `testStartStopDatanodeStateMachine` starts the daemon, waits until one SCM connection is registered, then stops it. `testDatanodeStateContext` manually executes INIT and RUNNING tasks, verifies endpoint states moving through GETVERSION, REGISTER, and heartbeat paths, and checks mock RPC counts. Failure tests set the datanode ID directory read-only or provide malformed SCM names and expect SHUTDOWN. The priority test waits for command-processing thread creation and checks priority ordering.

State and persistence behavior: It writes a datanode ID file for the context test and initializes datanode layout storage before running SCM version negotiation. Runtime state includes state-machine context state, endpoint state, stored SCM version responses, RPC counts, and daemon thread lifecycle.

Dependencies and integration points: The tests integrate local RPC servers, datanode identity persistence, SCM connection manager, endpoint task scheduling, layout storage, volume choosing policy configuration, and thread management. They exercise real `DatanodeStateMachine` behavior rather than only mocks.

Risks: Timing is a key risk because waits depend on RPC server startup, endpoint transitions, and threads. File permission behavior for read-only directories can vary by environment. Invalid configuration coverage is table-driven but limited to selected malformed `OZONE_SCM_NAMES` strings.

Test signals: Strong signals include one connection manager entry, daemon stopped flag, expected INIT/RUNNING/SHUTDOWN states, endpoint GETVERSION and REGISTER states, non-null version response, exact mock RPC and heartbeat counts, default `CapacityVolumeChoosingPolicy`, and state-machine thread priority greater than command-processing thread priority.
