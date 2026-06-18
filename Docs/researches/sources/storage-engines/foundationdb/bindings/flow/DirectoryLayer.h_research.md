## sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.h

Purpose: declares the Flow `DirectoryLayer` implementation of `IDirectory` plus the nested `Node` traversal helper and constants defining directory metadata layout.

Important APIs and types: public methods implement create/open/createOrOpen/exists/list/move/remove against `Reference<Transaction>`. Constants include default node/content subspaces, `PARTITION_LAYER`, metadata keys, version, and allocator key. `Node` carries directory layer reference, optional node subspace, current path, target path, layer metadata, and loaded flag.

Control flow: public APIs dispatch to private `createOrOpenInternal`, `checkVersion`, `initializeDirectory`, `nodeWithPrefix`, `contentsOfNode`, and path helpers. `Node` supports lazy metadata loading and partition detection.

State and persistence: fields `rootNode`, `nodeSubspace`, `contentSubspace`, `allocator`, `allowManualPrefixes`, and `path` define where directory metadata and content live and whether callers can pick prefixes.

Dependencies and integration points: includes `IDirectory.h`, `DirectorySubspace.h`, and `HighContentionAllocator.h`. Friend access from `DirectoryPartition` and helper actors relies on exposed internals.

Risks: the header exposes many internals as public/commented private, so external code can depend on implementation details. `Path` uses vectors of `Standalone<StringRef>`, requiring careful arena ownership.

Test signals: API surface mirrors other FoundationDB directory layer bindings and is used by `DirectoryTester`.
