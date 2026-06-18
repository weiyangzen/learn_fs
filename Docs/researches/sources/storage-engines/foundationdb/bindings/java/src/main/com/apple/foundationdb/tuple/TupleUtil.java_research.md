<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java

## Purpose
`TupleUtil` is the package-private encoder/decoder and comparator implementation behind `Tuple`.

## Important APIs, Types, And Functions
It defines tuple type codes, `DecodeState`, `EncodeState`, floating-point bit transforms, integer byte sizing, versionstamp offset adjustment, `getCodeFor`, overloaded `encode`, `decode`, `compareItems`, `unpack`, `pack`, `packWithVersionstamp`, `getPackedSize`, and `hasIncompleteVersionstamp`.

## Control Flow
Encoding dispatches by Java type, writes type codes, escapes embedded null bytes in strings/byte arrays, transforms floats/doubles for sortable byte order, encodes integers with variable-length positive/negative forms, and records exactly one incomplete versionstamp position. Decoding reads type codes, validates truncation, reverses escaping and numeric transforms, validates UTF-8, and recursively decodes nested tuples. Comparison mirrors encoded order without necessarily packing.

## State And Persistence Behavior
The utility is stateless except for local encode/decode state. Its byte output is the persistent key format used in FoundationDB. Versionstamp suffix size depends on `FDB.instance().getAPIVersion()`: older APIs use a 2-byte offset and newer APIs use a 4-byte offset.

## Dependencies And Integration Points
It depends on `FDB` for API version, `ByteArrayUtil` for null escaping and unsigned comparison, `StringUtil`, `Versionstamp`, `IterableComparator`, `UUID`, `BigInteger`, and `ByteBuffer`. `Tuple`, `Subspace`, directory code, and tests rely on exact compatibility.

## Risks And Test Signals
This is compatibility-critical. Risks include type-code drift, buffer size mismatch, malformed UTF-8 handling, nested null escaping, BigInteger range/order edge cases, float NaN ordering, old versus new versionstamp offset formats, and unsupported type errors. Tests should include official tuple conformance vectors, fuzz round trips, compare-versus-packed-order checks, API-version-specific versionstamp tests, and malformed/truncated input cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java -->
