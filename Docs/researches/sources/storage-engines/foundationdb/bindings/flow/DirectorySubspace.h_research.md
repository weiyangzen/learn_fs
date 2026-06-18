## sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.h

Purpose: declares the combined `IDirectory` and `Subspace` handle returned by directory layer operations.

Important APIs and types: exposes directory lifecycle operations relative to this directory, subspace functionality inherited from `Subspace`, and accessors `getDirectoryLayer`, `getLayer`, and `getPath`. Protected helpers `getPartitionSubpath` and `getDirectoryLayerForPath` allow partition-specific behavior.

Control flow: callers can treat normal directory handles as subspaces for packing/unpacking keys, or as directories for nested operations.

State and persistence: stores `Reference<DirectoryLayer> directoryLayer`, absolute `Path path`, and layer metadata string. Raw prefix is owned by the `Subspace` base class.

Dependencies and integration points: includes `IDirectory.h`, `DirectoryLayer.h`, and `Subspace.h`; returned by `DirectoryLayer::contentsOfNode`.

Risks: multiple inheritance means object lifetime and virtual dispatch must remain stable across `IDirectory` and `Subspace` uses. Path and layer values are copied `Standalone`/vector data to preserve memory safety.

Test signals: all directory handles in tester flows are instances of this class or `DirectoryPartition`.
