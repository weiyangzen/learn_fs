# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TuplePackingTest.java

## Purpose
`TuplePackingTest` validates tuple packing behavior, especially packed-size accounting, add/merge APIs, incomplete versionstamp rules, malformed sequence rejection, UTF-8 validation, prefix packing, and versionstamp position adjustment.

## Important APIs, Types, and Functions
It uses `Tuple`, `Versionstamp`, `ByteArrayUtil`, `Subspace`, `FDBLibraryRule`, parameterized method sources `baseAddCartesianProduct`, `twoIncomplete`, `malformedSequences`, and `wellFormedSequences`, plus reflection against `Tuple.memoizedPackedSize` to exercise validation paths.

## Control Flow
Tests combine base tuples with many item types and assert `getPackedSize`, `pack`, `packWithVersionstamp`, `addAll`, `addObject`, `fromStream`, and prefix packing behave consistently. Versionstamp tests assert incomplete versionstamps cannot be packed normally, exactly one incomplete versionstamp can be packed with appended little-endian position metadata, and two incomplete versionstamps are rejected. Malformed sequence tests feed truncated or invalid encoded byte strings into `Tuple.fromBytes`. Malformed string tests ensure invalid UTF-16 surrogate combinations cannot be sized or packed, including after reflective memoized-size manipulation.

## State and Persistence Behavior
State is local to tests except for `FDBLibraryRule.current()`, which selects/preloads the API version for versionstamp-sensitive behavior. No database data is written.

## Dependencies and Integration Points
The test is a compatibility guard for the tuple layer used by subspaces, directory keys, Java binding tests, and cross-language FoundationDB tuple encoding. It also depends on Java reflection and privileged access for one validation path.

## Risks and Edge Cases
The test intentionally creates a large byte array of size `0x0100fe` to check ambiguous versionstamp representation, which is memory-sensitive but bounded. Reflection against a private field is brittle under tuple implementation refactors. Some assumptions skip cases based on version/API state.

## Test Signals
Passing provides strong evidence that tuple packing size, byte representation, versionstamp handling, malformed input rejection, and prefix/subspace interactions remain compatible.
