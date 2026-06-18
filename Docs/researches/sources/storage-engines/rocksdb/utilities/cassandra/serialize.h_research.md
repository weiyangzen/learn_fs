# sources/storage-engines/rocksdb/utilities/cassandra/serialize.h

## Purpose
This header provides small template specializations that serialize and deserialize signed integer fields in Cassandra row values as big-endian bytes.

## Important APIs, Types, and Functions
Generic declarations exist for `Serialize<T>` and `Deserialize<T>`, with inline specializations for `int8_t`, `int32_t`, and `int64_t`. Constants `kCharMask` and `kBitsPerByte` drive byte extraction and reconstruction.

## Control Flow
Serialization appends the high-order byte first and the low-order byte last for 32-bit and 64-bit values; 8-bit values append a single byte. Deserialization reads bytes from `src + offset`, casts each byte to `unsigned char` for the wider types, shifts them into position, and ORs them into the result.

## State and Persistence Behavior
The functions mutate only the destination string supplied by the caller and read from raw source memory supplied by the caller. They define the durable byte order for Cassandra row-value fields.

## Dependencies and Integration Points
The header depends only on standard integer/string headers and `rocksdb/rocksdb_namespace.h`. It is used by `format.cc` and tested by `cassandra_serialize_test.cc`.

## Risks and Edge Cases
There is no bounds checking on `src` or `offset`. Unsupported template types have declarations but no definitions, causing link failures if accidentally used. Right-shifting negative signed integers during serialization can be implementation-sensitive. The anonymous namespace constants in a header create internal-linkage copies in each translation unit, which is acceptable here but unusual.

## Test Signals
`cassandra_serialize_test.cc` verifies exact byte sequences and offset-aware round trips for representative signed values. Additional fuzzing with random values would strengthen confidence in round-trip symmetry.
