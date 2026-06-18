## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerDiff.java

Purpose: this test class validates the container Merkle tree diff algorithm used to decide whether a local container needs repair relative to a peer checksum tree.

Important APIs and tests: parameterized mismatch cases cover missing blocks, missing chunks, and corrupt chunks. Tests call `ContainerChecksumTreeManager.read()` and `diff()`, then assert `ContainerDiffReport` contents and metrics. Additional tests cover no-diff cases and deleted-block filtering.

Control flow and state: one direction of mismatch matters: if the local tree is missing or corrupt relative to the peer, the diff reports repair work. If only the peer is missing or corrupt relative to local, this local diff reports no repair because the peer should generate its own diff. Deleted blocks in the peer or local tree suppress repair entries for those blocks.

Persistence and integration: tests write local checksum protobufs to temp files using helpers, construct peer `ContainerChecksumInfo` in memory, and verify `ContainerChecksumTreeManager` metrics such as repair/no-repair counts and identified missing/corrupt counts.

Risks and test signals: the tests define subtle asymmetric semantics. A regression that treats peer deficiencies as local repair work would cause unnecessary repairs. Deletion handling is critical because deleted blocks must not be resurrected by reconciliation.
