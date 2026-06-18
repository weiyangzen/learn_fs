<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go

Purpose: small internal representation of a directory metadata node while resolving paths.

Important APIs: `node` stores a metadata subspace, resolved path, original target path, and cached layer future. `exists` checks for non-nil subspace. `prefetchMetadata` starts the layer read. `layer` lazily reads `node.subspace.Sub("layer")`. `isInPartition` checks whether the node exists, has layer `partition`, and whether empty subpaths are included. `getPartitionSubpath` returns unresolved path suffix. `getContents` materializes the node as a `DirectorySubspace`.

Control flow: `directoryLayer.find` creates nodes as it walks child mappings. A node can stop resolution early when it does not exist or when it is a partition boundary.

State and persistence: reads only the node `layer` key. It caches the `FutureByteSlice`, not the decoded byte slice, so repeated calls share the same FDB future.

Dependencies and integration: uses `fdb.FutureByteSlice` and `subspace.Subspace`; tightly coupled to `directory_layer.go` partition and contents logic.

Risks: `isInPartition` calls `MustGet`, so FDB read errors panic. Calling `isInPartition` before `prefetchMetadata`/`layer` would dereference nil `_layer`; current callers prefetch or call layer during find. Partition suffix slicing assumes `targetPath` is at least as long as `path`.

Test signals: indirect; valuable tests would simulate missing nodes, normal nodes, partition boundaries, and layer-read errors in transactional wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/node.go -->
