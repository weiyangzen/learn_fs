<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java

## Purpose
`Subspace` is the Java binding helper for namespacing FoundationDB keys with a raw byte prefix plus an optional tuple prefix.

## Important APIs, Types, And Functions
Constructors accept no prefix, a `Tuple`, raw bytes, or both. Core methods are `get`, `subspace`, `getKey`, `pack`, `packWithVersionstamp`, `unpack`, `range`, `contains`, `equals`, `hashCode`, and `toString`.

## Control Flow
Construction joins raw bytes with `prefix.pack()`, rejecting incomplete versionstamps through tuple packing. Packing delegates to `Tuple.pack(rawPrefix)`. Unpack first checks `contains` and decodes after `rawPrefix.length`. Range delegates to tuple range with the raw prefix.

## State And Persistence Behavior
The only state is `rawPrefix`, held as a final byte array. Returned `pack()` values are copies, but the raw-byte constructor and join behavior should be considered carefully for caller mutation of input arrays before construction completes. No database writes occur; the class defines key layout for callers.

## Dependencies And Integration Points
It depends on `Range`, `Tuple`, `Versionstamp`, and `ByteArrayUtil`. `DirectorySubspace` extends it, tuple tests exercise it, and directory code uses subspaces for metadata and content.

## Risks And Test Signals
Risks include prefix containment mistakes, unpacking keys outside the subspace, incomplete versionstamp use in constructor prefixes, and raw byte aliasing assumptions. Tests should cover pack/unpack round trips, range bounds, nested subspaces, `packWithVersionstamp` prefix offset adjustment, and equality/hash consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java -->
