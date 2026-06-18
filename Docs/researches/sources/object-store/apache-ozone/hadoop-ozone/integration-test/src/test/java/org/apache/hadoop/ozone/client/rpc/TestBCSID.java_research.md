# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBCSID.java

Purpose: This focused integration test verifies that a container's block commit sequence ID (BCSID) is propagated from a committed key into OM key metadata, reported by the datanode container report, and reloaded correctly after a datanode restart.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneClientFactory`, `TestDataUtil.createKey`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `ReplicationConfig.fromTypeAndFactor`, `RatisReplicationConfig`, and datanode internals reached through `getDatanodeStateMachine().getContainer().getContainerSet().getContainer(...).getContainerReport().getBlockCommitSequenceId()`.

Control flow: `init` configures short container-report, command-status, heartbeat, and stale-node intervals, disables safe-mode pipeline creation, starts a one-datanode mini cluster, creates an RPC client, and creates a `bcsid` volume and bucket. `testBCSID` writes a RATIS/ONE key named `ratis`, looks the key up through OM, asserts there is exactly one latest block location, reads the same container's BCSID from the datanode container report, compares it with `OmKeyLocationInfo.getBlockCommitSequenceId()`, restarts the datanode with persistence, and checks the reported BCSID is unchanged.

State and persistence behavior: The key write commits a block to one datanode container and persists its BCSID in both container metadata and OM key-location metadata. The restart assertion verifies the datanode reload path preserves the persisted BCSID rather than resetting it or relying only on memory.

Dependencies and integration points: This test connects OM key lookup state with datanode container report state and SCM-facing report metadata. It relies on a real datanode container set, real key allocation/commit, and cluster restart support rather than mocks.

Risks: The single-datanode cluster makes the state easy to reason about but only covers RATIS/ONE. The assertions assume the created key lands in one block and that the datanode restart path completes cleanly before the report is queried. The test reaches through internal datanode structures, so refactors of container accessors can affect it even if public behavior is unchanged.

Test signals: The core signals are one block location, a datanode-reported BCSID greater than zero, equality between datanode report BCSID and OM `OmKeyLocationInfo` BCSID, and equality again after `restartHddsDatanode(0, true)`.
