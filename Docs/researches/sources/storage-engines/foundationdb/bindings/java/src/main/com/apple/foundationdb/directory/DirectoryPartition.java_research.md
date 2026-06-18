<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java

## Purpose
`DirectoryPartition` represents a directory-layer partition root. It is a directory handle but intentionally not a usable content subspace; clients must create children under it.

## Important APIs, Types, And Functions
The constructor creates a nested `DirectoryLayer` with node subspace `prefix + DEFAULT_NODE_SUBSPACE_PREFIX` and content subspace `prefix`, sets that nested layer path, and records the parent layer. It overrides all subspace operations (`get`, `getKey`, `pack`, `unpack`, `range`, `contains`, `subspace`) to throw `UnsupportedOperationException`. `getLayerForPath` routes empty-path operations to the parent layer and child operations to the partition layer.

## Control Flow
The class delegates directory operations through inherited `DirectorySubspace` behavior, except empty-path remove/exists/move context is resolved back to the parent layer. Direct content key operations fail immediately.

## State And Persistence Behavior
Persistent partition metadata is created by `DirectoryLayer` using the special `PARTITION_LAYER` byte string. This wrapper changes namespace layout so descendant directories allocate inside the partition prefix.

## Dependencies And Integration Points
It extends `DirectorySubspace`, depends on `DirectoryLayer`, `Subspace`, `Tuple`, `Range`, and `ByteArrayUtil.join`, and is constructed by `DirectoryLayer.contentsOfNode` when node layer equals `partition`.

## Risks And Test Signals
Risks include accidentally treating partition roots as content subspaces, incorrect empty-subpath routing, and equality/hash behavior needing to account for parent layer. Tests should assert every forbidden subspace method throws, child directory operations succeed, and cross-partition moves are rejected.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java -->
