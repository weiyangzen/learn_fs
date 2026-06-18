<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java

Purpose: This test verifies `ContainerStateMap.getContainerIDs` filtering and pagination by container lifecycle state.

Important APIs and types: It uses `ContainerStateMap`, `ContainerInfo`, `ContainerID`, `HddsProtos.LifeCycleState`, and `StandaloneReplicationConfig` with replication factor THREE.

Control flow: The test builds ten containers with known IDs and states, adds them to a new `ContainerStateMap`, and queries IDs by state. It asserts there are four `OPEN` and four `CLOSED` containers, then verifies pagination for closed containers from `ContainerID.MIN` and from `ContainerID.valueOf(7)` with limit three.

State and persistence behavior: State is an in-memory state map populated from constructed `ContainerInfo` objects. No persistence is touched.

Dependencies and integration points: This guards the SCM container-state indexing behavior used by list and scan operations that page through container IDs by lifecycle state.

Risks: Off-by-one errors in start ID or limit handling would affect API pagination. The test only exercises adds and reads, not state transitions or removal.

Test signals: Exact result sizes for state-filtered lookup and limit-bounded pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/states/TestContainerStateMap.java -->
