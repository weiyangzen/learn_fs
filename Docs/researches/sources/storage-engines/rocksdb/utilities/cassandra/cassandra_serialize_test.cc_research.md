# sources/storage-engines/rocksdb/utilities/cassandra/cassandra_serialize_test.cc

## Purpose
This file is the focused unit test for Cassandra utility integer serialization. It verifies that the helpers in `utilities/cassandra/serialize.h` encode and decode signed `int8_t`, `int32_t`, and `int64_t` values as big-endian byte strings.

## Important APIs, Types, and Functions
The tests use RocksDB's `test_util/testharness.h` macros and directly call the template specializations `Serialize<T>(T, std::string*)` and `Deserialize<T>(const char*, std::size_t)`. Test cases are split by width and direction: `SerializeI64`, `DeserializeI64`, `SerializeI32`, `DeserializeI32`, `SerializeI8`, and `DeserializeI8`. The file-level `main` installs the RocksDB stack trace handler, initializes GoogleTest, and runs all tests.

## Control Flow
Each serialization test clears or appends to a `std::string`, serializes representative values, and compares the exact byte sequence. Each deserialization test records the current string size as an offset, appends a serialized value, and deserializes from that offset to prove offset-aware decoding works when multiple values are packed together.

## State and Persistence Behavior
The tests are purely in-memory. The only mutable state is a local `std::string dest` reused across assertions. No filesystem or database state is created.

## Dependencies and Integration Points
This is the lowest-level signal for Cassandra row encoding because all higher-level row, column, tombstone, and merge operator serialization depends on these byte helpers. It also indirectly constrains RocksDB/Cassandra compatibility by making byte order stable across host endianness.

## Risks and Edge Cases
The tests cover zero, one, negative one, positive max, and negative boundary-like values for each width. They do not test unsigned types, arbitrary offsets beyond the append pattern, invalid/truncated buffers, or template instantiation failures for unsupported types. The negative integer serialization relies on implementation behavior of right-shifting signed values, which is common but worth noting for portability-sensitive changes.

## Test Signals
Passing this file confirms exact big-endian encoding for signed integer values used by Cassandra value formats. Failures would usually indicate a wire-format regression that could make persisted Cassandra merge operands unreadable or incorrectly ordered.
