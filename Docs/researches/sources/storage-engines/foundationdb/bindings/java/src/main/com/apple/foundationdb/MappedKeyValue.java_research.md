# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedKeyValue.java

## Purpose
`MappedKeyValue` extends `KeyValue` with mapper range metadata and nested range results returned by FoundationDB mapped range queries.

## Important APIs, Types, And Functions
It stores `rangeBegin`, `rangeEnd`, and `rangeResult`. Getters expose each. `fromBytes(byte[], int[])` decodes concatenated native bytes and lengths into key, value, mapped range bounds, and nested `KeyValue`s. `takeBytes` advances a small `Offset` cursor. Equality, hash, and string formatting include all fields.

## Control Flow
JNI array-based mapped range results call `fromBytes`; direct-buffer results construct `MappedKeyValue` directly. Consumers iterate through `MappedRangeQuery` or call `asList`.

## State And Persistence Behavior
The object stores byte-array and list references. It is field-immutable but not deeply immutable because arrays and the list can be mutated externally.

## Dependencies And Integration Points
It depends on `KeyValue`, `ByteArrayUtil`, and is used by `MappedRangeResult`, `MappedRangeQuery`, and `ReadTransaction.getMappedRange`.

## Risks And Edge Cases
The serialization format is coupled to native `FDBMappedKeyValue`. Malformed lengths throw exceptions or copy out of bounds. The raw `rangeResult` list can be null or mutable.

## Test Signals
Tests should cover decoding valid mapped rows with zero and multiple nested results, malformed length counts, equality/hash including nested results, and direct constructor behavior.
