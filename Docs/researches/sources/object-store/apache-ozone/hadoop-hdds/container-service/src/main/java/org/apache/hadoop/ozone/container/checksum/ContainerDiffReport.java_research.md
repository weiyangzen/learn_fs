# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerDiffReport.java

## Purpose
Mutable summary of differences between a local container checksum tree and a peer's tree, describing what repair actions the local replica needs.

## Important APIs, Types, And Functions
APIs add and read missing block trees, missing chunk trees by block ID, corrupt chunk trees by block ID, diverged deleted blocks, aggregate counts, `needsRepair`, and `toString`. Nested `DeletedBlock` stores block ID and data checksum.

## Control Flow
`ContainerChecksumTreeManager.diff` populates the report while walking peer/local Merkle trees. Repair code can inspect the grouped lists and maps to request or apply missing/corrupt data and deleted-block metadata.

## State And Persistence
State is in-memory lists/maps scoped to one container ID. No persistence unless serialized/logged by higher layers.

## Dependencies And Integration Points
Depends on `ContainerProtos.BlockMerkleTree` and `ChunkMerkleTree` protobuf messages.

## Risks
The report is mutable and not synchronized. Method `getNumdivergedDeletedBlocks` has a lowercase spelling inconsistency. It stores peer tree protobufs directly, so callers should treat them as immutable values.

## Test Signals
Signals include `needsRepair` true/false, accurate aggregate counts, readable `toString`, and reconciliation tests covering all four difference classes.
