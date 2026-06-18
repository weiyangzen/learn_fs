## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerMerkleTreeWriter.java

Purpose: this test class validates `ContainerMerkleTreeWriter`, including checksum construction, ordering, duplicate handling, deleted-block semantics, proto round trips, and merge/update conflict rules.

Important APIs and tests: tests cover empty trees, one-chunk trees, missing chunks, block ID inclusion in checksums, identical-block determinism, non-contiguous block IDs, append behavior, `setDeletedBlock`, constructor from proto, `addDeletedBlocks`, and `update(existingTree)`.

Control flow and state: expected trees are built independently by hashing chunk checksum bytes, block IDs plus chunk checksums, and block checksums through the same checksum implementation. Writer output is compared for sorted block IDs and chunk offsets. Duplicate chunks overwrite existing entries by offset. Deleted blocks remove chunk trees and carry deleted checksums. Merge tests define precedence: existing deleted blocks override writer live blocks, writer live blocks override existing live blocks, writer deleted blocks override existing live blocks, and writer deleted checksums override existing deleted checksums.

Persistence and integration: this class is in-memory only, but it defines the protobuf structure written later by `ContainerChecksumTreeManager`. It integrates with `ContainerProtos`, `BlockData`, and checksum byte-buffer implementation.

Risks and test signals: checksum semantics intentionally include block ID, preventing identical content under different block IDs from colliding. Deleted-block precedence is central to avoiding deleted data resurrection during checksum file updates.
