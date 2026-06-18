## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeTestUtils.java

Purpose: this final utility class provides shared builders and assertions for container checksum tree, Merkle tree, diff, and reconciliation tests.

Important APIs and functions: helpers include `assertTreesSortedAndMatch`, `buildChunk`, `readChecksumFile`, `buildTestTree`, `getDeletedBlockData`, `buildTestTreeWithMismatches`, `updateTreeProto`, `assertContainerDiffMatch`, `containerChecksumFileExists`, `verifyAllDataChecksumsMatch`, and `buildBlockData`.

Control flow and state: the builders synthesize deterministic chunk, block, and container Merkle structures from Ozone configuration chunk size and checksum settings. Mismatch introduction mutates a tree builder by removing blocks, removing chunks, or corrupting chunk checksum values while recording the expected `ContainerDiffReport`. File helpers read and write the `.tree` checksum protobuf directly. `verifyAllDataChecksumsMatch()` compares in-memory container data, checksum file data, and RocksDB metadata.

Persistence and integration: utilities interact with actual container checksum files under container metadata paths and RocksDB through `BlockUtils.getDB`. They integrate with `ContainerChecksumTreeManager`, `ContainerMerkleTreeWriter`, `ContainerDiffReport`, `HddsDatanodeService`, and key-value container data.

Risks and test signals: the direct file helpers intentionally bypass production synchronization, so they are test-only. Random checksum mutation prevents reliance on exact corrupt values. Assertions enforce sorted block IDs and chunk offsets, making ordering part of the contract.
