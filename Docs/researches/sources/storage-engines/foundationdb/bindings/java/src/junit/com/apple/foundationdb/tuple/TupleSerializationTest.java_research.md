# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleSerializationTest.java

## Purpose
`TupleSerializationTest` verifies exact tuple serialization bytes, deserialization round trips, offset/length validation for `fromBytes`, and `packInto(ByteBuffer)` behavior.

## Important APIs, Types, and Functions
It defines a `TupleSerialization` holder, a large `serializedForms` corpus, `offsetAndLengthTuples`, and tests for packed size, packing, depacking, invalid offsets/lengths, partial tuple unpacking, combined tuple unpacking, and ByteBuffer packing. It uses `Tuple`, `Versionstamp`, `ByteArrayUtil`, `FDBLibraryRule`, `ByteBuffer`, `ByteOrder`, and `BufferOverflowException`.

## Control Flow
Parameterized tests compare each tuple's `getPackedSize` and `pack` output to exact expected bytes, then unpack and compare tuple equality. Offset/length tests pack a combined tuple and assert invalid slices fail while zero-length at array end is valid. Pairwise slice tests unpack adjacent tuple encodings and compare to expected combined tuples. `testPackIntoBuffer` packs into buffers with exact size, extra capacity, prefilled prefix bytes, too-small capacity, copied tuple state, and incomplete versionstamp input.

## State and Persistence Behavior
All tuple data is in-memory. `FDBLibraryRule.current()` selects/preloads the FDB API for tests that may require current tuple/versionstamp semantics.

## Dependencies and Integration Points
This is a precise compatibility contract for the Java tuple encoding format used for FoundationDB keys and cross-language interoperability.

## Risks and Edge Cases
The serialized corpus is intentionally brittle: any encoding change breaks tests, which is desirable for compatibility but requires careful migration. `packInto` tests ensure buffer byte order is preserved, but only a small tuple is used for buffer cases.

## Test Signals
Passing shows exact byte-level compatibility for many primitive, binary, string, nested tuple, UUID, boolean, and versionstamp encodings, plus robust slice validation and ByteBuffer packing behavior.
