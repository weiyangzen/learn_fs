## sources/storage-engines/foundationdb/bindings/flow/DirectoryPartition.h

Purpose: represents a directory layer partition. A partition can be navigated as an `IDirectory`, but cannot be used directly as a `Subspace`.

Important APIs and types: `DirectoryPartition` derives from `DirectorySubspace`, constructs a nested `DirectoryLayer` rooted under the partition prefix, stores the parent directory layer, and overrides `key`, `contains`, `pack`, `unpack`, `range`, `subspace`, and `get` to throw `cannot_use_partition_as_subspace`.

Control flow: constructor builds a nested directory layer with node subspace `DEFAULT_NODE_SUBSPACE_PREFIX.withPrefix(prefix)` and content subspace `prefix`, sets nested layer path to the partition path, and marks layer as `PARTITION_LAYER`. `getDirectoryLayerForPath` returns the parent for empty path operations and the nested layer for subpaths.

State and persistence: partition metadata lives in the parent directory, while subdirectories/content under the partition use nested metadata and content prefixes rooted under the partition prefix.

Dependencies and integration points: tightly coupled to `DirectoryLayer`, `DirectorySubspace`, and directory operation delegation in `DirectoryLayer.cpp`.

Risks: path delegation rules are subtle; using a partition as a normal subspace is intentionally blocked to avoid ambiguous content ranges.

Test signals: directory tests should verify partition creation, operations inside partitions, and errors for subspace methods.
