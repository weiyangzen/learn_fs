<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java

Purpose: This compact suite verifies `ContainerReportValidator.validate` for EC container replica indexes reported by datanodes.

Important APIs and types: It uses `ContainerReportValidator`, `ContainerReplicaProto`, `ContainerInfo`, `ContainerID`, `DatanodeDetails`, `ECReplicationConfig(3,2)`, `PipelineID`, `HddsTestUtils.getECContainer`, and `HddsTestUtils.createContainerReplica`.

Control flow: A helper builds a closed container replica protobuf for a given replica index and datanode. The valid test creates a 3+2 EC container and asserts index `1` is accepted. The parameterized invalid test checks indexes `0`, `6`, `100`, and `-1` are rejected for a five-replica EC layout.

State and persistence behavior: There is no persistence. The test state is the EC replication config, replica index field, container ID, and datanode UUID in the report protobuf.

Dependencies and integration points: This protects SCM's container report ingestion path, where datanode-reported EC replica indexes must fit the container's data+parity index range.

Risks: If EC index rules change or become layout-specific, the hard-coded invalid range must be updated. The suite does not cover Ratis containers or mismatched datanode identity behavior.

Test signals: `validate` returns true for an in-range EC replica index and false for zero, out-of-range, large, and negative indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/report/TestContainerReportValidator.java -->
