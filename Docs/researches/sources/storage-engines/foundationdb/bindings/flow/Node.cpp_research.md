## sources/storage-engines/foundationdb/bindings/flow/Node.cpp

Purpose: implements `DirectoryLayer::Node`, the traversal state object used while resolving paths in the directory layer.

Important APIs and functions: constructor stores directory layer, optional subspace, current path, target path, and initializes `loadedMetadata=false`. `exists` checks subspace presence. `loadMetadata` reads the node layer key. `isInPartition`, `getPartitionSubpath`, and `getContents` interpret loaded metadata.

Control flow: `find` in `DirectoryLayer.cpp` constructs and updates `Node` instances while walking path components. `loadMetadata` must keep the node alive while its future is outstanding, as noted by the comment. Once metadata is loaded, partition checks can decide whether to delegate.

State and persistence: reads layer metadata from `subspace.pack(LAYER_KEY)` and caches it in the node. Does not write database state.

Dependencies and integration points: includes `DirectoryLayer.h`, uses transaction `get`, `DirectoryLayer::contentsOfNode`, and `PARTITION_LAYER`.

Risks: callers must not call `isInPartition` or `getContents` before metadata is loaded; assertions enforce this in debug builds. Async load on a pointer to `Node` requires lifetime discipline.

Test signals: all directory operations exercise node traversal and partition detection.
