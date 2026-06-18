# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/utils/ClusterContainersUtil.java

Purpose: test utility for locating, corrupting, verifying, and retrieving container data on disk inside a `MiniOzoneCluster`.

Important APIs/types/functions: `getChunksLocationPath`, `corruptData`, `verifyOnDiskData`, `getContainerByID`. It uses `OzoneKeyDetails`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, `BlockData`, `KeyValueContainerLocationUtil`, Apache Commons `FileUtils`, and DN `ContainerSet`.

Control flow: `getChunksLocationPath` requires the provided `OzoneKey` to be `OzoneKeyDetails`, extracts the first key location's container ID and local ID, opens the key-value container DB, verifies the block exists via block key lookup, then computes the chunks directory from the container volume root, cluster ID and container ID. `corruptData` gets that directory and overwrites every top-level chunk file with `"corrupted data"`. `verifyOnDiskData` reads every top-level chunk file and returns false on first content mismatch. `getContainerByID` scans all datanodes and returns the first matching container from each DN state machine's container set.

State and persistence: this utility directly reads and writes on-disk chunk files and opens the container DB. Corruption is destructive to the mini-cluster's test data and intended only for tests that isolate their cluster state.

Dependencies and integration points: MiniOzoneCluster configuration and cluster ID, datanode container sets, key-value container DB layout, block metadata keys, and chunk path layout helper. It bridges Ozone client metadata (`OzoneKeyDetails`) to DN local storage.

Risks: only the first key location is considered, so multi-block or EC keys may not be fully handled. Chunk file listing is non-recursive. `verifyOnDiskData` reads using default charset while corruption writes UTF-8 bytes, which is fine for ASCII test strings but not arbitrary binary chunks. Direct file mutation can invalidate checksums and affect later tests.

Test signals: not a test class; downstream tests use it to assert a block exists, force corruption, verify chunk content, or locate a container replica.
