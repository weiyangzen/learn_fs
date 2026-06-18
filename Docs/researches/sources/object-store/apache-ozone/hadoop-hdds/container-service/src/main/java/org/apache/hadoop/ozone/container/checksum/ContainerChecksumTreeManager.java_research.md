# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerChecksumTreeManager.java

## Purpose
Coordinator for reading, writing, diffing, and exposing persisted per-container checksum Merkle trees on a datanode.

## Important APIs, Types, And Functions
Important APIs include constructor, `stop`, `diff`, `read`, `updateTree`, `addDeletedBlocks`, `getContainerChecksumInfo`, `readChecksumInfo`, `getDataChecksum`, `hasDataChecksum`, and checksum file path helpers. It uses striped locks and `ContainerMerkleTreeMetrics`.

## Control Flow
Diff validates local and peer checksum info, rejects mismatched container IDs, compares sorted block lists, then sorted chunk lists, reporting missing blocks/chunks, corrupt local chunks when the peer chunk is healthy, and diverged deleted-block metadata. Writes take a per-container lock, read existing data or empty state, merge through a provided function, serialize to a tmp file, and atomically move it into place.

## State And Persistence
Persistent state is `<containerId>.tree` under the container metadata path plus tmp files during writes. In-memory state is the striped lock set and metrics object. Readers do not lock because writes use atomic rename.

## Dependencies And Integration Points
Depends on datanode configuration for lock stripes, protobuf `ContainerChecksumInfo`, container data paths, `ContainerMerkleTreeWriter`, block data, Ratis `ByteString`, and metrics utilities.

## Risks
Atomic move may fail on unsupported filesystems. `readOrCreate` overwrites unreadable trees on update, which favors recovery but can lose corrupted forensic data. Diff assumes block IDs and chunk offsets are sorted. Skipping unhealthy peer chunks avoids copying bad data but may leave local repair incomplete until another peer is queried.

## Test Signals
Signals include checksum file read/write latency and failure metrics, diff metrics, missing/corrupt/diverged report counts, concurrent updates to the same and different containers, absent tree file behavior, and reconciliation with deleted blocks.
