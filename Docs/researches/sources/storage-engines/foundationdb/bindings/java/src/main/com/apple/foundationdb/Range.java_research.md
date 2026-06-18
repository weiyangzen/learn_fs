# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Range.java

## Purpose
`Range` is the public value type for an inclusive begin key and exclusive end key in FoundationDB keyspace.

## Important APIs, Types, And Functions
The constructor stores `begin` and `end` as public final byte arrays. `startsWith(byte[])` builds a prefix range using `ByteArrayUtil.strinc`. `equals`, `hashCode`, and `toString` provide content-based behavior and printable formatting.

## Control Flow
Read and clear overloads accept `Range` and unpack begin/end. Prefix range construction validates non-null prefix and calculates the first key after the prefix.

## State And Persistence Behavior
`Range` stores byte-array references without copying; fields are final but array contents are mutable.

## Dependencies And Integration Points
It is used by `ReadTransaction`, `Transaction`, `KeyRangeArrayResult`, and range/clear helper overloads. It depends on `ByteArrayUtil`.

## Risks And Edge Cases
Mutating `begin` or `end` after construction changes equality/hash and API behavior. `startsWith` relies on `strinc` behavior for all-0xff prefixes, which may throw depending on utility semantics.

## Test Signals
Tests should cover equality/hash, null prefix rejection, prefix range boundaries, binary string formatting, and mutation implications.
