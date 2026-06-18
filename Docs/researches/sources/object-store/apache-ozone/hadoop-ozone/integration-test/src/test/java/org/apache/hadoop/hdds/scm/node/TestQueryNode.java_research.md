<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java

Purpose: Tests SCM node query results for stale and dead nodes after datanode shutdown.

Important APIs and types: Uses `MiniOzoneCluster`, `ContainerOperationClient.queryNode`, `HddsProtos.QueryScope.CLUSTER`, `NodeState.STALE`, `NodeState.DEAD`, and SCM node-count APIs.

Control flow: Setup starts a five-datanode cluster with one-second reports, three-second stale interval, six-second dead interval, and relaxed Ratis pipeline limit. The test asynchronously shuts down two datanodes, waits until querying stale plus dead returns two total nodes, waits for SCM node count of dead nodes to reach two, then asserts stale query returns zero and dead query returns two.

State and persistence behavior: Runtime node health state transitions from healthy to stale/dead based on missing heartbeats. No durable state is under direct test, though the cluster holds normal SCM metadata while running.

Dependencies and integration points: Covers `ContainerOperationClient` query path, SCM node manager health tracking, datanode shutdown behavior, and timing configuration for node-state transitions.

Risks: The executor is not explicitly shut down. The wait from mixed stale/dead to all dead assumes interval timing allows final assertions within four seconds after the intermediate condition. The client is constructed from the same configuration rather than cluster-provided RPC address changes.

Test signals: Signals are stale-plus-dead query count reaching two, SCM dead node count reaching two, final stale query count zero, and final dead query count two.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestQueryNode.java -->
