## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestContainerChecksumTreeManager.java

Purpose: this test class validates `ContainerChecksumTreeManager` file creation, read/modify/write behavior, corruption recovery, deleted-block merging, metrics, and path compatibility.

Important APIs and tests: it mocks `KeyValueContainerData` with container ID and metadata path, uses `ContainerChecksumTreeManager`, and checks methods such as `updateTree`, `addDeletedBlocks`, `read`, `diff`, `hasDataChecksum`, `getContainerChecksumFile`, and metric counters.

Control flow and state: tests write empty trees, write deleted-block-only trees, write normal trees, deduplicate and sort deleted blocks, preserve deleted blocks across tree writes, preserve trees across deleted-block writes, and assert read/write/create latency metrics change. Failure tests make tmp-file writes fail, corrupt final files with invalid bytes, and truncate final files to empty protobufs, then verify recovery.

Persistence and integration: the checksum file name is asserted as `<containerID>.tree` under the metadata path, explicitly protecting on-disk compatibility. Writes use temporary files and swaps, and reads use protobuf parsing. The diff failure test verifies a bad peer checksum increments failure metrics.

Risks and test signals: permission manipulation may behave differently on some filesystems. The tests strongly signal that production must tolerate corrupted or empty checksum files and keep existing valid files intact on tmp write failure.
