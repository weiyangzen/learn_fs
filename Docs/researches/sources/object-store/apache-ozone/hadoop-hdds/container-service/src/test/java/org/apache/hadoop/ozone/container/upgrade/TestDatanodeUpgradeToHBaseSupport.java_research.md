## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDatanodeUpgradeToHBaseSupport.java

Purpose: Tests behavior gates around finalizing from `HADOOP_PRC_PORTS_IN_DATANODEDETAILS` to `HBASE_SUPPORT`.

Important APIs/types/functions: `DatanodeStateMachine.finalizeUpgrade`, `HDDSLayoutFeature.HBASE_SUPPORT`, `ContainerDispatcher`, `UpgradeTestHelper.putBlock`, `finalizeBlock`, `closeContainer`, and `ContainerProtos.Result.UNSUPPORTED_REQUEST`.

Control flow: Each test starts SCM and a pre-finalized datanode, creates a container, attempts a feature-gated operation before finalization and expects `UNSUPPORTED_REQUEST`, closes the container, finalizes, creates a new container, and verifies the same operation succeeds after finalization. Covered gates are incremental chunk list support and block finalization.

State and persistence behavior: Real temp datanode metadata/volume state and container writes through dispatcher.

Dependencies and integration points: Validates layout-feature gating across container command dispatch, not just version flags.

Risks and test signals: Good compatibility signal for pre-finalized clusters. It assumes containers must be closed before finalization can proceed.
