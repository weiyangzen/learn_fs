<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java

## Purpose
`Tuple` is the public sortable typed key container for the Java binding. It serializes Java values into FoundationDB's cross-language tuple encoding and compares in key order.

## Important APIs, Types, And Functions
It supports `String`, `byte[]`, numeric types, `BigInteger`, `Float`, `Double`, `UUID`, `Boolean`, `Versionstamp`, nested `List`/`Tuple`, and `null`. APIs include typed `add` methods, `addObject`, `addAll`, `pack`, `packInto`, `packWithVersionstamp`, `fromBytes`, `fromItems`, `fromList`, `fromStream`, typed getters, `range`, `compareTo`, `equals`, `hashCode`, `toString`, `getPackedSize`, and `hasIncompleteVersionstamp`.

## Control Flow
Public add methods create new `Tuple` instances with appended or merged element lists. Packing validates incomplete versionstamp rules, memoizes packed bytes, and delegates encoding to `TupleUtil`. Versionstamp packing appends an offset suffix and adjusts it when a prefix is added. Deserialization slices/copies bytes, unpacks through `TupleUtil`, and memoizes the original packed representation.

## State And Persistence Behavior
The object is effectively immutable through public APIs but stores mutable internal memoization: packed bytes, hash, and packed size. `getItems` copies the element list, while `getRawItems` is package-private. Packed keys are the persistence format used by FoundationDB clients; incomplete versionstamps are only valid for versionstamped mutations.

## Dependencies And Integration Points
It depends on `TupleUtil`, `ByteArrayUtil`, `IterableComparator`, `Range`, `Versionstamp`, and `Subspace`. Directory metadata, examples, tests, and application key modeling all use this class.

## Risks And Test Signals
Risks include non-thread-safe memoization, mutable nested lists or byte arrays altering semantics after tuple creation, numeric conversion surprises for generic `Number`, incomplete versionstamp misuse, packed-size bugs, and equality based on tuple byte order. Tests should cover cross-language encoding vectors, all supported types, null handling, nested values, versionstamp suffix offsets for old/new API versions, range bounds, hash/equality memoization, and malformed byte input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java -->
