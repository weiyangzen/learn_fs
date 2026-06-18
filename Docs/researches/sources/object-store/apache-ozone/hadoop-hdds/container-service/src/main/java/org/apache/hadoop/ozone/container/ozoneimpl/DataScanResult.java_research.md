## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/DataScanResult.java

Purpose: Represents a full container data scan result, including metadata/data errors and the container Merkle tree observed during the scan.

Important APIs and functions: `unhealthyMetadata()` converts a failed metadata scan into a data scan result with an empty tree. `deleted()` returns an interned deleted result. `fromErrors()` builds a result with supplied errors and tree. `getDataTree()` exposes the checksum tree writer.

Control flow and state: Extends `MetadataScanResult` and adds final `ContainerMerkleTreeWriter` state. The deleted result is interned because it has no per-scan data; healthy results are not interned because each has its own tree.

Persistence and dependencies: The result itself is not persistent, but `ContainerScanHelper` uses the tree to update container checksum metadata. Depends on Guava preconditions and `ContainerMerkleTreeWriter`.

Risks: `unhealthyMetadata()` requires the metadata result to have errors; using it with healthy/deleted results is invalid. Empty tree for metadata failure intentionally signals no data was scanned. The tree object must reflect exactly the bytes scanned before checksum persistence.

Test signals: Healthy/error/deleted result construction, unhealthy metadata conversion precondition, tree propagation to controller updates, deleted interning, and helper behavior for transient/non-transient data errors.
