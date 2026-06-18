<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java

## Purpose
`DirectoryLayer` is the main Java implementation of FoundationDB directories. It maps human-readable hierarchical paths to compact binary content prefixes and stores directory metadata in a node subspace.

## Important APIs, Types, And Functions
Constructors accept node/content `Subspace`s and an `allowManualPrefixes` flag. Static helpers create layers with custom node or content subspaces, and `getDefault` returns the singleton default layer using node prefix `0xFE` and empty content prefix. Public operations implement `Directory`: `createOrOpen`, `open`, `create`, `move`, `remove`, `removeIfExists`, `list`, and `exists`. Key internals include `createOrOpenInternal`, `createInternal`, `openInternal`, `removeInternal`, `removeRecursive`, `isPrefixFree`, `checkVersion`, `checkOrWriteVersion`, `NodeFinder`, `Node`, `PrefixFinder`, and `HighContentionAllocator`.

## Control Flow
Read paths first validate directory-layer version and walk subdirectory links with `NodeFinder`. Create/open either opens an existing node, delegates into a partition, or allocates/validates a prefix and writes parent-child and layer metadata. Move checks version, rejects moving root or a directory into its own subtree, resolves old and new nodes, delegates partition-internal moves, writes a destination parent link, and removes the old parent link. Remove validates non-root paths, delegates into partitions when needed, clears content and metadata ranges, then recursively clears descendant nodes.

## State And Persistence Behavior
Persistent metadata lives under `nodeSubspace`: root version, high-contention allocation counters/recent markers, layer entries, and subdirectory pointers keyed by `SUB_DIR_KEY` plus child name. Content lives under allocated prefixes in `contentSubspace`. `checkOrWriteVersion` initializes `{1,0,0}` in little-endian ints; `VersionCheck` blocks future major versions and `WritableVersionCheck` makes future minor versions read-only. Automatic prefixes are allocated with transaction conflict management and then checked against existing key ranges and directory metadata. Manual prefixes are rejected unless enabled and also must be prefix-free.

## Dependencies And Integration Points
The implementation depends on FoundationDB `Transaction`, `ReadTransaction`, `Range`, `MutationType.ADD`, `AsyncUtil`, `AsyncIterator`, `Subspace`, `Tuple`, and `ByteArrayUtil`. `DirectorySubspace` and `DirectoryPartition` are returned handles. The high-contention allocator is integrated with FDB conflict ranges and snapshot reads.

## Risks And Edge Cases
Prefix allocation is correctness-critical: collisions with manually allocated prefixes or existing data become `IllegalStateException`/`IllegalArgumentException`. `NodeFinder` must stop at partitions and load metadata before partition tests. Recursive removal clears opened directories while stale clients may still write under old prefixes. The allocator synchronizes on a class object to avoid transaction-local races, with comments noting this is not ideal. Path lists and layer arrays are not always defensively copied internally. Root open/remove/move behavior is intentionally special.

## Test Signals
Strong tests include duplicate create, open missing, layer mismatch, version compatibility, manual prefix allow/deny, automatic prefix collision detection, remove recursion, list ordering/content, exists across normal and partition directories, move into self, move to missing parent, move across partitions, and high-concurrency creation under contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java -->
