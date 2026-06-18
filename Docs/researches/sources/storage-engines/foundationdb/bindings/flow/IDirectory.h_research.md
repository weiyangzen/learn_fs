## sources/storage-engines/foundationdb/bindings/flow/IDirectory.h

Purpose: abstract interface for Flow directory-layer operations.

Important APIs and types: defines `Path` as `std::vector<Standalone<StringRef>>` and pure virtual methods for create, open, createOrOpen, exists, list, move, moveTo, remove, removeIfExists, getDirectoryLayer, getLayer, and getPath.

Control flow: concrete `DirectoryLayer`, `DirectorySubspace`, and `DirectoryPartition` implementations provide async methods returning Flow `Future`s and directory/subspace references.

State and persistence: interface only; persistent effects are defined by implementations.

Dependencies and integration points: includes Flow primitives and `fdb_flow.h`, forward declares directory classes, and provides the shared contract used by tester instruction functions.

Risks: all operations are transaction-scoped; callers must commit separately. `Path` component ownership through `Standalone<StringRef>` must remain intact across async boundaries.

Test signals: `DirectoryTester.cpp` interacts mostly through this interface, so it is the central compatibility surface.
