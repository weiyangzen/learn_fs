# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerReplicationEndToEnd.java

## Purpose
`TestContainerReplicationEndToEnd` simulates a complete closed-container replication path. It verifies that after one original replica node is lost, Replication Manager copies a closed container to a new datanode and the key remains readable from the replicated container after the original pipeline nodes are shut down.

## Important APIs, types, and functions
The fixture uses `MiniOzoneCluster` with four datanodes, starts Replication Manager, and tunes heartbeat, container report, stale/dead node, pipeline destroy, follower slowness, and no-leader timeouts. The test uses `XceiverClientManager`/`XceiverClientSpi` to send a raw `CloseContainer` command, `ContainerID`, `PipelineID`, `Pipeline`, `ContainerOperation` protos, `OmKeyLocationInfo`, and `GenericTestUtils.waitFor`.

## Control flow
The test creates a RATIS/THREE key, writes and flushes `"ratis"`, captures its single key location, resolves the container and pipeline from SCM, and closes the key. If SCM has not already moved the container to `CLOSING` or `CLOSED`, the test finalizes it. It then sends an explicit close-container command to the first pipeline node and waits for SCM to report `CLOSED`.

After shutting down the old replica node, it selects a datanode not in the original pipeline and waits until that datanode's container set contains the container. It checks the new replica has a positive block commit sequence ID. Finally it shuts down the other original pipeline nodes and validates the key data, forcing reads to use the newly replicated container.

## State and persistence behavior
The test observes SCM container lifecycle state, datanode container sets, replica placement, and block commit sequence IDs. Persistence is proven by reading the key after original replicas are unavailable. State movement depends on container reports and Replication Manager intervals.

## Dependencies and integration points
This is an end-to-end path across Ozone client writes, OM key metadata, SCM container and pipeline managers, datanode close-container handling, Replication Manager, and client reads. It uses raw container protocol commands rather than only public object-store APIs.

## Risks and test signals
The test uses sleeps based on `containerReportInterval`, so timing can be sensitive. The decisive signals are SCM state `CLOSED`, the new datanode acquiring the container, positive BCSID on the replicated container, and successful read after all original pipeline nodes are stopped.
